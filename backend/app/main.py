from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv()

from app.auth.routes import router as auth_router

app = FastAPI()

app.include_router(auth_router)

@app.get("/")
def root():
    return {"status": "Backend running"}

