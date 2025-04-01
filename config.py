import os
import time
import secrets
from cryptography.fernet import Fernet

# Application settings
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
fernet = Fernet(ENCRYPTION_KEY)

# Security settings
TOKEN_EXPIRY_MINUTES = 60
MAX_API_REQUESTS_PER_MINUTE = 60
MAX_ROOM_CREATION_PER_HOUR = 10
MAX_FILE_SIZE_MB = 5
PASSWORD_MIN_LENGTH = 8
ROOM_ID_LENGTH = 5
ENABLE_XSS_PROTECTION = True
ENABLE_RATE_LIMITING = True
SECURE_COOKIES = True

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip'}

# Data storage
chat_rooms = {}
room_passwords = {}
room_verified_ips = {}
user_profiles = {}
online_users = {}
message_reactions = {}
typing_users = {}
user_socket_map = {}
room_files = {}  # To store file information per room
message_read_status = {}  # To track which messages have been read by which users

# Server settings
HOST = '0.0.0.0'
PORT = 10000
DEBUG = True 