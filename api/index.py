from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
# from dotenv import load_dotenv # Dotenv is often not needed in Vercel prod if vars are set in UI, but keep it if you want

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
    img = Image.open(image_path)
    # Apply EXIF orientation if present
    try:
        from PIL import ImageOps
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass  # No EXIF data or already correctly oriented
    img = img.convert('RGB')
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
        
    
    return base64_images

# Add this block to allow connection from Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://cheer-machine.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.get("/api/decrypt/{passkey}")
def get_decrypt(passkey: str):
    # FIX: Get the directory where THIS script (index.py) lives
    current_dir = os.path.dirname(__file__)
    
    # FIX: Look for images in the same folder (api/encrypted-images)
    input_path = os.path.join(current_dir, "encrypted-images")
    
    # Debug print (logs appear in Vercel dashboard)
    print(f"Looking for images in: {input_path}")
    
    base64_images = decrypt_image_with_password(
        input_path=input_path,
        password_text=passkey,
        salt_hex=os.environ.get("SALT"), # Ensure these are set in Vercel Project Settings!
        nonce_hex=os.environ.get("NONCE")
    )
    
    return {"images": base64_images}