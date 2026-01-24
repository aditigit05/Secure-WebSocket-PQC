from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.auth.store import session_store

from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os



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
    
    # 🔐 STEP 4: Derive AES key from shared secret
    aes_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"secure-chat-step4",
    ).derive(shared_secret)

    aesgcm = AESGCM(aes_key)
    print("[STEP 4] AES key derived")
    
    await ws.send_text("SECURE_CHANNEL_READY")
    print(f"[SECURE] channel ready for user {user_id}")



    print(f"[STEP 3] Shared secret established for user {user_id}")
    print(f"[STEP 3] Secret length: {len(shared_secret)} bytes")

    print("[SECURE] AES-GCM channel active")

    try:
        while True:
            encrypted_b64 = await ws.receive_text()
            encrypted = base64.b64decode(encrypted_b64)

            nonce = encrypted[:12]
            ciphertext = encrypted[12:]

            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            message = plaintext.decode()

            print(f"[DECRYPTED from {user_id}]: {message}")

            # Encrypt echo back
            resp_nonce = os.urandom(12)
            resp_ct = aesgcm.encrypt(
                resp_nonce,
                f"echo: {message}".encode(),
                None
            )

            await ws.send_text(
                base64.b64encode(resp_nonce + resp_ct).decode()
            )

    except WebSocketDisconnect:
        print(f"[DISCONNECTED] {user_id}")
