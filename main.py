from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, FileResponse
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64
import os
from io import BytesIO
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import shutil
from fastapi.middleware.cors import CORSMiddleware
import webbrowser
import threading


templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (can be restricted to specific URLs)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Function to generate a key from a password and salt
def generate_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# Encrypt file endpoint
@app.post("/encrypt/")
async def encrypt_file(password: str = Form(...), file: UploadFile = File(...)):
    print("🔐 ENCRYPT endpoint hit")
    print(f"Received file: {file.filename}")
    print(f"Received password: {password}")

    file_content = await file.read()

    # Extract file extension
    _, ext = os.path.splitext(file.filename)
    ext_bytes = ext.encode("utf-8")
    ext_len = len(ext_bytes).to_bytes(1, byteorder='big')  # 1 byte for extension length

    # Generate salt and key
    salt = os.urandom(16)
    key = generate_key(password, salt)

    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(file_content)

    # Save file: [ext_len][ext][salt][encrypted_data]
    full_encrypted = ext_len + ext_bytes + salt + encrypted_data

    encrypted_directory = "encrypted_files"
    os.makedirs(encrypted_directory, exist_ok=True)

    encrypted_file_path = os.path.join(encrypted_directory, f"{file.filename}.enc")

    with open(encrypted_file_path, "wb") as enc_file:
        enc_file.write(full_encrypted)

    return {"encrypted_file": encrypted_file_path}


# Decrypt file endpoint
@app.post("/decrypt/")
async def decrypt_file(password: str = Form(...), file: UploadFile = File(...)):
    print("🔓 DECRYPT endpoint hit")
    print(f"Received file: {file.filename}")
    print(f"Received password: {password}")

    file_content = await file.read()

    # Extract original extension
    ext_len = file_content[0]
    ext = file_content[1:1+ext_len].decode("utf-8")

    # Extract salt and encrypted data
    salt = file_content[1+ext_len:1+ext_len+16]
    encrypted_data = file_content[1+ext_len+16:]

    key = generate_key(password, salt)
    fernet = Fernet(key)

    try:
        decrypted_data = fernet.decrypt(encrypted_data)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid password or corrupted file.")

    decrypted_directory = "decrypted_files"
    os.makedirs(decrypted_directory, exist_ok=True)

    original_name = os.path.splitext(file.filename)[0]
    decrypted_file_path = os.path.join(decrypted_directory, f"{original_name}{ext}")

    with open(decrypted_file_path, "wb") as dec_file:
        dec_file.write(decrypted_data)

    return {"decrypted_file": decrypted_file_path}




