from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.auth.store import session_store

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    token = ws.query_params.get("token")

    if not token or token not in session_store:
        await ws.close(code=1008)
        return

    user_id = session_store[token]["user_id"]

    await ws.accept()
    await ws.send_text(f"Connected as user {user_id}")

    try:
        while True:
            msg = await ws.receive_text()
            await ws.send_text(f"echo: {msg}")
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
