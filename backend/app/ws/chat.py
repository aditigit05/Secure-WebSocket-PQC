from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.auth.store import session_store

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import base64
import json

router = APIRouter()

# user_id -> WebSocket
connections = {}


@router.websocket("/ws/chat")
async def chat_ws(ws: WebSocket):
    token = ws.query_params.get("token")

    if not token or token not in session_store:
        await ws.close(code=1008)
        return

    user_id = session_store[token]["user_id"]
    await ws.accept()

    # ---------- KEY EXCHANGE (UNCHANGED) ----------

    client_pub_b64 = await ws.receive_text()
    client_pub = x25519.X25519PublicKey.from_public_bytes(
        base64.b64decode(client_pub_b64)
    )

    server_private = x25519.X25519PrivateKey.generate()
    server_public = server_private.public_key()

    await ws.send_text(
        base64.b64encode(server_public.public_bytes_raw()).decode()
    )

    shared_secret = server_private.exchange(client_pub)

    # Derive AES key (server does NOT use it further)
    HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"secure-chat-step4",
    ).derive(shared_secret)

    await ws.send_text("SECURE_CHANNEL_READY")
    connections[user_id] = ws

    print(f"[SECURE] E2EE channel ready for user {user_id}")
    print("[SECURE] Server running in BLIND RELAY mode")

    # ---------- BLIND RELAY (NO CRYPTO HERE) ----------

    try:
        while True:
            packet = await ws.receive_text()
            data = json.loads(packet)

            target_id = data["to"]
            ciphertext = data["data"]

            target_ws = connections.get(target_id)
            if target_ws:
                await target_ws.send_text(ciphertext)

    except WebSocketDisconnect:
        connections.pop(user_id, None)
        print(f"[DISCONNECTED] {user_id}")
