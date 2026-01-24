from websocket import WebSocket
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import json, base64

TOKEN = "nBzYqOivKCYTYXkjDP-9bY1gukIZXxH53WcS05NZUF4"


AES_KEY = b"\x01" * 32   

aesgcm = AESGCM(AES_KEY)

ws = WebSocket()
ws.connect(f"ws://127.0.0.1:8000/ws/chat?token={TOKEN}")

print("[B] Connected. Waiting for encrypted messages...")

while True:
    msg = json.loads(ws.recv())
    data = base64.b64decode(msg["payload"])

    nonce = data[:12]
    ct = data[12:]

    plaintext = aesgcm.decrypt(nonce, ct, None)
    print("[B] Decrypted message:", plaintext.decode())
