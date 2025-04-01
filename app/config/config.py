import os
from datetime import datetime

JWT_SECRET = "your-secret-key-here"
ENCRYPTION_KEY = b'your-encryption-key-here'

PORT = 10000
HOST = '0.0.0.0'

MAX_MESSAGES_PER_ROOM = 100

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%I:%M %p"