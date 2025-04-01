import jwt
from datetime import datetime
from flask import request
from cryptography.fernet import Fernet
from app.config.config import JWT_SECRET, ENCRYPTION_KEY, DATE_FORMAT, TIME_FORMAT

# Initialize encryption
fernet = Fernet(ENCRYPTION_KEY)

def generate_token(room_id):
    """Generate a JWT token for authentication"""
    payload = {
        "room_id": room_id,
        "exp": datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token):
    """Verify JWT token"""
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded["room_id"]
    except:
        return None

def get_client_ip():
    """Get client's IP address"""
    return request.headers.get("X-Forwarded-For", request.remote_addr)

def encrypt_message(message):
    """Encrypt a message"""
    return fernet.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message):
    """Decrypt a message"""
    return fernet.decrypt(encrypted_message.encode()).decode()

def get_current_time():
    """Get current time in required format"""
    current_time = datetime.now()
    return {
        'date': current_time.strftime(DATE_FORMAT),
        'time': current_time.strftime(TIME_FORMAT),
        'timestamp': int(current_time.timestamp() * 1000)
    } 