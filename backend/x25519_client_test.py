from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from websocket import WebSocket
import base64
import os
import json


TOKEN = "CpY9C3IGm2Js3N_nZNOm2ZF-1_B7MeE0q_uSPzf3iYk"
MY_USER_ID = "8bd5367b-78b5-415e-886a-b62894520adb"

ws = WebSocket()
ws.connect(f"ws://127.0.0.1:8000/ws/chat?token={TOKEN}")

# ---------- KEY EXCHANGE ----------

client_private = x25519.X25519PrivateKey.generate()
client_public = client_private.public_key()

ws.send(
    base64.b64encode(client_public.public_bytes_raw()).decode()
)

server_pub_b64 = ws.recv()
server_public = x25519.X25519PublicKey.from_public_bytes(
    base64.b64decode(server_pub_b64)
)

shared_secret = client_private.exchange(server_public)

msg = ws.recv()
if msg != "SECURE_CHANNEL_READY":
    raise Exception("Secure channel not confirmed")

print("[SECURE] Channel ready")

# ---------- AES KEY DERIVATION ----------

aes_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"secure-chat-step4",
).derive(shared_secret)

aesgcm = AESGCM(aes_key)
print("[SECURE] AES-GCM ready (client-side only)")

# ---------- SEND ENCRYPTED MESSAGE ----------

plaintext = b"hello from true E2EE client"

nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, plaintext, None)
payload = base64.b64encode(nonce + ciphertext).decode()

ws.send(json.dumps({
    "to": MY_USER_ID,
    "data": payload
}))

# ---------- RECEIVE + DECRYPT ----------

incoming = ws.recv()
raw = base64.b64decode(incoming)

n = raw[:12]
ct = raw[12:]

decrypted = aesgcm.decrypt(n, ct, None)
print("Decrypted message:", decrypted.decode())

ws.close()
