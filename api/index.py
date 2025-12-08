from http.server import BaseHTTPRequestHandler
import json
import os
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from urllib.parse import urlparse

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Turns a text password into a 32-byte binary key using a KDF.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
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
        for filename in sorted(os.listdir(input_path)):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                pixels, _ = get_image_data(os.path.join(input_path, filename))
                flat_pixels = pixels.tobytes()
                images.append([flat_pixels, pixels])

    # Reconstruct Salt, Key, and Nonce
    salt = bytes.fromhex(salt_hex)
    nonce = bytes.fromhex(nonce_hex)
    key = derive_key(password_text, salt)

    base64_images = []
    
    for i, image_data in enumerate(images):
        flat_pixels = image_data[0]
        pixels = image_data[1]
        
        # Decrypt
        cipher = Cipher(algorithms.AES(key), modes.CTR(nonce), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_bytes = decryptor.update(flat_pixels) + decryptor.finalize()

        # Convert to base64
        decrypted_pixels = np.frombuffer(decrypted_bytes, dtype=np.uint8)
        decrypted_pixels = decrypted_pixels.reshape(pixels.shape)
        img = Image.fromarray(decrypted_pixels, 'RGB')
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        base64_images.append(f"data:image/png;base64,{img_base64}")
    
    return base64_images

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL path
        parsed_path = urlparse(self.path)
        path_parts = parsed_path.path.strip('/').split('/')
        
        # Set CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
        
        # Check if path matches /api/decrypt/{passkey}
        if len(path_parts) >= 3 and path_parts[0] == 'api' and path_parts[1] == 'decrypt':
            passkey = path_parts[2]
            
            # Find the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Try different paths depending on deployment
            possible_paths = [
                os.path.join(current_dir, "..", "public", "encrypted-images"),
                "/var/task/public/encrypted-images",
            ]
            
            input_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    input_path = path
                    break
            
            if not input_path:
                response = {"error": "Image directory not found", "checked_paths": possible_paths}
                self.wfile.write(json.dumps(response).encode())
                return
            
            salt_hex = os.environ.get("SALT")
            nonce_hex = os.environ.get("NONCE")
            
            if not salt_hex or not nonce_hex:
                response = {"error": "Missing environment variables"}
                self.wfile.write(json.dumps(response).encode())
                return
            
            try:
                base64_images = decrypt_image_with_password(
                    input_path=input_path,
                    password_text=passkey,
                    salt_hex=salt_hex,
                    nonce_hex=nonce_hex
                )
                
                response = {"images": base64_images}
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                response = {"error": str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            response = {"error": "Invalid path"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()
