from websocket import WebSocket
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import json, base64, os

TOKEN = "vY_mMdMjUwUXQpK5lYPnFOeni0UO9LWj8nStL8j-4XU"
TARGET_USER_ID = "e44715b3-607e-4c1b-aec9-9f75cf096b4c"


AES_KEY = b"\x01" * 32

aesgcm = AESGCM(AES_KEY)

ws = WebSocket()
ws.connect(f"ws://127.0.0.1:8000/ws/chat?token={TOKEN}")

plaintext = b"HELLO FROM USER A"

nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext, None)
payload = base64.b64encode(nonce + ciphertext).decode()

ws.send(json.dumps({
    "to": TARGET_USER_ID,
    "payload": payload
}))

print("[A] Encrypted message sent")
ws.close()
