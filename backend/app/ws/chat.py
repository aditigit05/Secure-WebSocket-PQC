from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.auth.store import session_store
import base64

router = APIRouter()

connections = {}  # user_id -> WebSocket

@router.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    token = ws.query_params.get("token")

    if not token or token not in session_store:
        await ws.close(code=1008)
        return

    user_id = session_store[token]["user_id"]
    await ws.accept()
    connections[user_id] = ws

    print(f"[CONNECTED] {user_id}")

    try:
        while True:
            encrypted_payload = await ws.receive_text()

            # 🔐 ROUTE ONLY (NO DECRYPTION)
            for uid, conn in connections.items():
                if uid != user_id:
                    await conn.send_text(encrypted_payload)

    except WebSocketDisconnect:
        connections.pop(user_id, None)
        print(f"[DISCONNECTED] {user_id}")
