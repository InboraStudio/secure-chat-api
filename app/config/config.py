import os
from datetime import datetime

# Security settings
JWT_SECRET = "your-secret-key-here"
ENCRYPTION_KEY = b'your-encryption-key-here'

# Server settings
PORT = 10000
HOST = '0.0.0.0'

# Message settings
MAX_MESSAGES_PER_ROOM = 100

# File paths
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Time format settings
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%I:%M %p" 