from websocket import WebSocket
import json
import base64
import os

TOKEN = "TzZXUAlboLeJj3mcWAbUMHvY4zvsD0xCK0Aj5VYV4a4"
TARGET_USER_ID = "5ff8ac39-2b3b-4f01-81d6-c88316bc0855"

ws = WebSocket()
ws.connect(f"ws://127.0.0.1:8000/ws/chat?token={TOKEN}")

# 🔐 Fake encrypted payload (random bytes)
ciphertext = base64.b64encode(os.urandom(32)).decode()

ws.send(json.dumps({
    "to": TARGET_USER_ID,
    "payload": ciphertext
}))

msg = json.loads(ws.recv())

print("Received payload (ciphertext only):", msg["payload"])

ws.close()
