from cryptography.hazmat.primitives.asymmetric import x25519
from websocket import WebSocket
import base64

TOKEN = "YK_jANA_1LIWURx24jMo7-IqNg0QHanv7KYS008p1Gs"

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

print("[STEP 3] Shared secret established")
print("[STEP 3] Secret length:", len(shared_secret))

# Plaintext test
ws.send("hello")
print("Server says:", ws.recv())

ws.close()
