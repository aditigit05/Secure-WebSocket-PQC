import secrets
import time

SESSION_EXPIRY_SECONDS = 900

def generate_session_token() ->str:
    return secrets.token_urlsafe(32)

def get_session_expiry() -> int:
    return int(time.time()) + SESSION_EXPIRY_SECONDS

def is_session_expired(expiry: int) -> bool:
    return time.time() > expiry
