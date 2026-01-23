from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.auth.store import session_store

from cryptography.hazmat.primitives.asymmetric import x25519
import base64

router = APIRouter()

@router.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    token = ws.query_params.get("token")

    if not token or token not in session_store:
        await ws.close(code=1008)
        return

    user_id = session_store[token]["user_id"]
    await ws.accept()

    # 🔐 STEP 3: Receive client public key
    client_pub_b64 = await ws.receive_text()
    client_pub_bytes = base64.b64decode(client_pub_b64)
    client_pub = x25519.X25519PublicKey.from_public_bytes(client_pub_bytes)

    # 🔐 Server generates keypair
    server_private = x25519.X25519PrivateKey.generate()
    server_public = server_private.public_key()

    # 🔐 Send server public key
    await ws.send_text(
        base64.b64encode(
            server_public.public_bytes_raw()
        ).decode()
    )

    # 🔐 Shared secret
    shared_secret = server_private.exchange(client_pub)

    print(f"[STEP 3] Shared secret established for user {user_id}")
    print(f"[STEP 3] Secret length: {len(shared_secret)} bytes")

    # Keep connection alive (no encryption yet)
    try:
        while True:
            msg = await ws.receive_text()
            await ws.send_text(f"echo: {msg}")
    except WebSocketDisconnect:
        print(f"User {user_id} disconnected")
