import jwt
import datetime
from flask import request
import socket
import config
import json

def allowed_file(filename):
    """Check if a filename has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def generate_token(room_id):
    """Generate JWT token for room access"""
    payload = {
        "room_id": room_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")

def verify_token(token):
    """Verify JWT token for room access"""
    try:
        decoded = jwt.decode(token, config.JWT_SECRET, algorithms=["HS256"])
        return decoded["room_id"]
    except:
        return None

def get_client_ip():
    """Get the client's IP address"""
    return request.headers.get("X-Forwarded-For", request.remote_addr)

def encrypt_message(message):
    """Encrypt a message using Fernet symmetric encryption"""
    try:
        if isinstance(message, dict):
            # Convert dictionary to string for encryption
            message_str = json.dumps(message)
            encrypted = config.fernet.encrypt(message_str.encode())
            return encrypted.decode()
        else:
            # Encrypt string messages
            encrypted = config.fernet.encrypt(str(message).encode())
            return encrypted.decode()
    except Exception as e:
        print(f"Encryption error: {e}")
        # Return original message if encryption fails
        return message

def decrypt_message(encrypted_message):
    """Decrypt a message using Fernet symmetric encryption"""
    try:
        decrypted = config.fernet.decrypt(encrypted_message.encode())
        decrypted_str = decrypted.decode()
        
        # Try to parse as JSON in case it was a dictionary
        try:
            return json.loads(decrypted_str)
        except:
            # Return as string if not valid JSON
            return decrypted_str
    except Exception as e:
        print(f"Decryption error: {e}")
        # Return original message if decryption fails
        return encrypted_message

def get_local_ip():
    """Get the local IP address of the server"""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def get_formatted_timestamp():
    """Get the current time formatted as a timestamp"""
    return int(datetime.datetime.now().timestamp() * 1000)

def format_date_time():
    """Get the current date and time formatted for messages"""
    now = datetime.datetime.now()
    formatted_date = now.strftime("%B %d, %Y")
    formatted_time = now.strftime("%I:%M %p")
    return formatted_date, formatted_time

def validate_room_id(room_id):
    """Validate that the room ID is a 5-digit number"""
    if not room_id:
        return False
    
    # Check if exactly 5 characters long and all digits
    if len(room_id) == 5 and room_id.isdigit():
        return True
    
    return False 