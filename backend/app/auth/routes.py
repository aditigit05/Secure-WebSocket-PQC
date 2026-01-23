from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from app.utils.email import send_otp_email
from app.auth.session import (
    generate_session_token,
    get_session_expiry,
)
from app.auth.otp import (
    generate_otp,
    hash_otp,
    verify_otp,
    get_expiry_timestamp,
    is_otp_expired
)
from app.auth.store import otp_store, session_store
from app.auth.dependencies import get_current_user
from app.auth.users import get_or_create_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

class OTPRequest(BaseModel):
    email: EmailStr
    
class OTPVerify(BaseModel):
    email: EmailStr
    otp: str

@router.post("/request-otp")
def request_otp(data: OTPRequest):
    otp = generate_otp()
    hashed = hash_otp(otp)
    expiry = get_expiry_timestamp()
    
    otp_store[data.email] = {
        "hashed_otp": hashed,
        "expiry": expiry,
        "attempts":0,
    }
    
    send_otp_email(data.email, otp)
    
    return {
        "message": "OTP sent to your email",
        "expires_in_seconds": 300,
    }
    
@router.post("/verify-otp")
def verify_otp_router(data: OTPVerify):
    record = otp_store.get(data.email)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not requested")
    
    if is_otp_expired(record["expiry"]):
        del otp_store[data.email]
        raise HTTPException(status_code=400, detail="OTP expired")
    
    if record["attempts"] >= 5:
        del otp_store[data.email]
        raise HTTPException(status_code=429, detail="Too many attempts")
    
    record["attempts"] += 1
    
    if not verify_otp(data.otp, record["hashed_otp"]):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    session_token = generate_session_token()
    expiry = get_session_expiry()
    
    user = get_or_create_user(data.email)
    
    session_store[session_token] = {
        "user_id": user["user_id"],
        "expiry": expiry,
    }
    
    print("SESSION_STORE AFTER LOGIN:", session_store)
    print("SESSION TOKEN ISSUED:", session_token)

    
    del otp_store[data.email]
    
    return {
        "message": "OTP varified successfully",
        "session_token": session_token,
        "expires_in_seconds": 900,
    }
    
@router.get("/me")
def get_me(current_user: str = Depends(get_current_user)):
    return{
        "user_id": current_user,
        "message": "You are authenticated"
    }