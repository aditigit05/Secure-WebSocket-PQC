from fastapi import Header, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import time 

from app.auth.store import session_store


security = HTTPBearer(auto_error= False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    # print("AUTH HEADER TOKEN RECEIVED:", credentials.credentials)
    # print("SESSION_STORE AT AUTH CHECK:", session_store)

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    token = credentials.credentials
    session = session_store.get(token)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token expired",
        )

    if "user_id" not in session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session format",
        )

    return session["user_id"]

