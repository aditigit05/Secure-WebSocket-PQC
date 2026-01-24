from fastapi import FastAPI
from app.auth.routes import router as auth_router
from app.ws.chat import router as ws_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(ws_router)

@app.get("/")
def root():
    return {"status": "Backend running"}
