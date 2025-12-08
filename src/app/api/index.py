from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <--- Import this

import os
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

app = FastAPI()

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Turns a text password into a 32-byte binary key using a KDF.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,       # We want exactly 32 bytes for AES-256
        salt=salt,       # Random data to make the hash unique
        iterations=100_000, # Slows down attackers trying to guess the password
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def get_image_data(image_path):
    img = Image.open(image_path).convert('RGB')
    pixels = np.array(img)
    return pixels, img.size
def decrypt_image_with_password(input_path, password_text, salt_hex, nonce_hex):
    
    images = []
    if os.path.isfile(input_path):
        pixels, _ = get_image_data(input_path)
        flat_pixels = pixels.tobytes()
        images.append([flat_pixels, pixels])
    else:
        for filename in os.listdir(input_path):
            pixels, _ = get_image_data(os.path.join(input_path, filename))
            flat_pixels = pixels.tobytes()
            images.append([flat_pixels, pixels])

    # 1. Reconstruct Salt, Key, and Nonce
    salt = bytes.fromhex(salt_hex)
    nonce = bytes.fromhex(nonce_hex)
    key = derive_key(password_text, salt)

    base64_images = []
    
    for i, image_data in enumerate(images):
        flat_pixels = image_data[0]
        pixels = image_data[1]
        
        # 2. Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_bytes = decryptor.update(flat_pixels) + decryptor.finalize()

        # 3. Convert to base64
        decrypted_pixels = np.frombuffer(decrypted_bytes, dtype=np.uint8)
        decrypted_pixels = decrypted_pixels.reshape(pixels.shape)
        img = Image.fromarray(decrypted_pixels, 'RGB')
        
        # Save to BytesIO buffer instead of file
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Encode to base64
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        base64_images.append(f"data:image/png;base64,{img_base64}")
        
        print(f"--- Decrypted image {i} ---")
    
    return base64_images

# Add this block to allow connection from Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # <--- The URL of your Next.js app
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],
)
@app.get("/api/decrypt/{passkey}")
def get_decrypt(passkey: str):
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    input_path = os.path.join(project_root, "public", "encrypted-images")
    
    base64_images = decrypt_image_with_password(
        input_path=input_path,
        password_text=passkey,
        salt_hex=os.environ.get("SALT"),
        nonce_hex=os.environ.get("NONCE")
    )
    
    return {"images": base64_images}