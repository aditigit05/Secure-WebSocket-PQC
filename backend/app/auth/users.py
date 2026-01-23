import uuid

user_store = {}
def get_or_create_user(email:str) -> dict:
    if email in user_store:
        return user_store[email]
    
    user = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "created_at": None,
    }
    user_store[email] = user
    
    return user