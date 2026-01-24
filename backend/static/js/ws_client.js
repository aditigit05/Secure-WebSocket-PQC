

let socket = null;
let secureReady = false;

async function connectWS(token) {
  socket = new WebSocket(`ws://127.0.0.1:8000/ws/chat?token=${token}`);

  socket.onopen = async () => {
    console.log("[WS] Connected");

    const kp = await window.cryptoClient.generateKeyPair();
    socket.send(kp.publicKeyB64);
  };

  socket.onmessage = async (event) => {
    if (!secureReady) {
      await window.cryptoClient.deriveAESKey(event.data);
      secureReady = true;
      console.log("[SECURE] Channel ready");
      return;
    }

    const msg = await window.cryptoClient.decryptMessage(event.data);
    addIncoming("Peer", msg);
  };

  socket.onerror = e => console.error("[WS ERROR]", e);
}

async function sendEncryptedMessage(text) {
  const cipher = await window.cryptoClient.encryptMessage(text);
  socket.send(cipher);
}
