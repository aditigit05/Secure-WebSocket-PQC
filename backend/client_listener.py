from websocket import WebSocket
import json

TOKEN = "BLMWLO3LHVcBJSXEZ5sQF_B8dFH35JWLFZDJ8BfEQdE"

ws = WebSocket()
ws.connect(f"ws://127.0.0.1:8000/ws/chat?token={TOKEN}")

print("[B] Connected. Waiting for messages...")

while True:
    msg = json.loads(ws.recv())
    print("[B] Received ciphertext:", msg["payload"])
