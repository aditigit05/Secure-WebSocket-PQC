import secrets
import time 
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

OTP_EXPIRY_SECONDS = 300

def generate_otp() -> str:
    return f"{secrets.randbelow(10**6):06d}"

def hash_otp(otp: str) -> str:
    return pwd_context.hash(otp)

def verify_otp(plain_otp: str, hashed_otp: str) ->bool:
    return pwd_context.verify(plain_otp, hashed_otp)

def get_expiry_timestamp() -> int:
    return int(time.time()) + OTP_EXPIRY_SECONDS

def is_otp_expired(expiry_timestamp: int) -> bool:
    return time.time() > expiry_timestamp
