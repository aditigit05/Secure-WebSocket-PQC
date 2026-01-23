import uuid
import time 

user_store = {}
def get_or_create_user(email:str) -> dict:
    if email in user_store:
        return user_store[email]
    
    user = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "created_at": int(time.time()),
    }
    user_store[email] = user
    
    return user