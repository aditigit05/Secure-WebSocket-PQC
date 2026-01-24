
const cryptoClient = (() => {
  let privateKey = null;
  let publicKey = null;
  let aesKey = null;

  async function generateKeyPair() {
    const kp = await window.crypto.subtle.generateKey(
      {
        name: "ECDH",
        namedCurve: "X25519"
      },
      true,
      ["deriveKey"]
    );

    privateKey = kp.privateKey;
    publicKey = kp.publicKey;

    const rawPub = await crypto.subtle.exportKey("raw", publicKey);
    const pubB64 = btoa(String.fromCharCode(...new Uint8Array(rawPub)));

    return { publicKeyB64: pubB64 };
  }

  async function deriveAESKey(serverPubB64) {
    const serverRaw = Uint8Array.from(atob(serverPubB64), c => c.charCodeAt(0));

    const serverPub = await crypto.subtle.importKey(
      "raw",
      serverRaw,
      { name: "ECDH", namedCurve: "X25519" },
      true,
      []
    );

    aesKey = await crypto.subtle.deriveKey(
      { name: "ECDH", public: serverPub },
      privateKey,
      { name: "AES-GCM", length: 256 },
      false,
      ["encrypt", "decrypt"]
    );
  }

  async function encryptMessage(text) {
    const nonce = crypto.getRandomValues(new Uint8Array(12));
    const encoded = new TextEncoder().encode(text);

    const cipher = await crypto.subtle.encrypt(
      { name: "AES-GCM", iv: nonce },
      aesKey,
      encoded
    );

    const payload = new Uint8Array([...nonce, ...new Uint8Array(cipher)]);
    return btoa(String.fromCharCode(...payload));
  }

  async function decryptMessage(b64) {
    const data = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    const nonce = data.slice(0, 12);
    const ciphertext = data.slice(12);

    const plain = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: nonce },
      aesKey,
      ciphertext
    );

    return new TextDecoder().decode(plain);
  }

  return {
    generateKeyPair,
    deriveAESKey,
    encryptMessage,
    decryptMessage
  };
})();

window.cryptoClient = cryptoClient;
