import jwt
from datetime import datetime
from flask import request
from cryptography.fernet import Fernet
from app.config.config import JWT_SECRET, ENCRYPTION_KEY, DATE_FORMAT, TIME_FORMAT

fernet = Fernet(ENCRYPTION_KEY)

def generate_token(room_id):
    payload = {
        "room_id": room_id,
        "exp": datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded["room_id"]
    except:
        return None

def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)

def encrypt_message(message):
    return fernet.encrypt(message.encode()).decode()

def decrypt_message(encrypted_message):
    return fernet.decrypt(encrypted_message.encode()).decode()

def get_current_time():
    current_time = datetime.now()
    return {
        'date': current_time.strftime(DATE_FORMAT),
        'time': current_time.strftime(TIME_FORMAT),
        'timestamp': int(current_time.timestamp() * 1000)
    }