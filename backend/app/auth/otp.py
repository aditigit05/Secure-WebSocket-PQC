import secrets
import time
import hmac
import hashlib
import os

OTP_EXPIRY_SECONDS = 300
OTP_SECRET = os.getenv("OTP_SECRET", "dev-secret-change-me")

def generate_otp() -> str:
    return f"{secrets.randbelow(10**6):6d}"

def hash_otp(otp:str) -> str:
    return hmac.new(
        OTP_SECRET.encode(),
        otp.encode(),
        hashlib.sha256
    ).hexdigest()
    
def verify_otp(plain_otp: str, hashed_otp: str) -> bool:
    calculated = hash_otp(plain_otp)
    return hmac.compare_digest(calculated, hashed_otp)

def get_expiry_timestamp() -> int:
    return int(time.time()) + OTP_EXPIRY_SECONDS

def is_otp_expired(expiry_timestamp: int) -> bool:
    return time.time() > expiry_timestamp