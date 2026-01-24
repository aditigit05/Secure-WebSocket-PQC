from cryptography.hazmat.primitives.asymmetric import x25519
from websocket import WebSocket
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes



TOKEN = "4g8D5nUMQrZF3oBNqXHRp9uLw60sbXWI8Z3kL-uXFuI"

ws = WebSocket()
ws.connect(f"ws://127.0.0.1:8000/ws/chat?token={TOKEN}")

# Client keypair
client_private = x25519.X25519PrivateKey.generate()
client_public = client_private.public_key()

# Send client public key
ws.send(
    base64.b64encode(
        client_public.public_bytes_raw()
    ).decode()
)

# Receive server public key
server_pub_b64 = ws.recv()
server_pub_bytes = base64.b64decode(server_pub_b64)
server_pub = x25519.X25519PublicKey.from_public_bytes(server_pub_bytes)

# Shared secret
shared_secret = client_private.exchange(server_pub)

print("[STEP 4] Shared secret established")

# 🔐 Wait for secure channel confirmation
msg = ws.recv()
if msg != "SECURE_CHANNEL_READY":
    raise Exception("Secure channel not confirmed")

print("[SECURE] Channel ready")

aes_key = HKDF(
    algorithm=hashes.SHA256(),
    length=32,
    salt=None,
    info=b"secure-chat-step4",
).derive(shared_secret)

aesgcm = AESGCM(aes_key)

print("[SECURE] AES-GCM ready")


print("[STEP 3] Shared secret established")
print("[STEP 3] Secret length:", len(shared_secret))

# # Plaintext test
# ws.send("hello")
# print("Server says:", ws.recv())

# Encrypt message
nonce = os.urandom(12)
ciphertext = aesgcm.encrypt(nonce, b"hello", None)
payload = base64.b64encode(nonce + ciphertext).decode()

ws.send(payload)

# Receive encrypted response
resp_b64 = ws.recv()
resp = base64.b64decode(resp_b64)

r_nonce = resp[:12]
r_ct = resp[12:]

plaintext = aesgcm.decrypt(r_nonce, r_ct, None)
print("Decrypted response:", plaintext.decode())

ws.close()
