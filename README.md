# 🔒 Secure Chat API

A modern, secure, end-to-end encrypted chat application with real-time messaging, file sharing, and multiple security features.

![Secure Chat](https://img.shields.io/badge/Secure%20Chat-1.0.0-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🔐 **End-to-End Encryption**: All messages are encrypted before storage
- 👤 **User Profiles**: Customizable user IDs, display names, and avatars
- 🚪 **Private Rooms**: Password-protected chat rooms
- 🌐 **IP Verification**: Room access restricted to verified IP addresses
- 📱 **Responsive Design**: Works on desktop and mobile devices
- 🖼️ **Media Sharing**: Send images and videos securely
- 📊 **Read Receipts**: See when messages have been read
- 💬 **Typing Indicators**: Know when someone is typing
- 👑 **Admin Controls**: Verify IPs, clear chat, delete rooms
- 🔄 **Real-time Updates**: Using WebSockets for instant communication
- 🔍 **Message Search**: Find past conversations easily
- 🖥️ **CLI Support**: Command-line interface for automation

## 🏗️ Architecture

The application follows a client-server architecture:

```
secure-chat-api/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── routes/                # API route handlers
│   ├── admin_routes.py    # Admin functionality
│   ├── auth_routes.py     # Authentication
│   ├── chat_routes.py     # Chat operations
│   ├── room_routes.py     # Room management
│   └── user_routes.py     # User profile management
├── utils/                 # Utility functions
│   ├── helpers.py         # Helper functions
│   └── middleware.py      # Request middleware
├── UI/                    # Frontend files
│   ├── css/               # Stylesheets
│   │   └── styles.css     # Main stylesheet
│   ├── js/                # JavaScript files
│   │   ├── chat.js        # Chat functionality
│   │   ├── main.js        # Main application logic
│   │   ├── media.js       # Media handling
│   │   └── setup.js       # Setup wizard
│   └── index.html         # Main HTML file
├── cli/                   # Command-line interface
│   ├── chat_cli.py        # CLI implementation
│   └── README.md          # CLI documentation
└── requirements.txt       # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.6 or higher
- Modern web browser
- Internet connection

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/DHIRAJ-GHOLAP/secure-chat-api.git
   cd secure-chat-api
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the server:
   ```bash
   python app.py
   ```

4. Access the web interface:
   ```
   http://localhost:10000
   ```

### CLI Usage

The project includes a command-line interface for automation:

```bash
# Install CLI requirements
python -m pip install requests

# Create a room
python cli/chat_cli.py create 12345 password123

# Send a message
python cli/chat_cli.py send 12345 "Hello world!" password123 --user-id yourname

# Get messages with read receipts
python cli/chat_cli.py get 12345 --password password123 --user-id yourname
```

For more details, see the [CLI documentation](cli/README.md).

## 🔐 Security Features

- **JWT Authentication**: Token-based authentication for API access
- **Message Encryption**: All messages encrypted using Fernet symmetric encryption
- **Password Protection**: Rooms secured with passwords
- **IP Verification**: Restrict room access to verified IP addresses
- **Access Control**: Multiple layers of authentication for sensitive operations
- **Read Receipts**: See who has read your messages with blue indicators
- **Rate Limiting**: Prevent abuse of API endpoints
- **Error Handling**: Secure error reporting without exposing sensitive information

## 📝 API Endpoints

### User Management

- `POST /user/profile`: Create or update user profile

### Room Management

- `POST /room/create`: Create or join a chat room
- `POST /room/<room_id>/verify_ip`: Verify an IP for room access

### Chat Operations

- `POST /chat/<room_id>`: Send a message to a room
- `GET /chat/<room_id>/messages`: Get messages from a room
- `POST /chat/<room_id>/clear`: Clear chat history
- `POST /chat/<room_id>/messages/mark_read`: Mark messages as read

### Admin Operations

- `POST /admin/verify_ip`: Admin verification of IPs
- `POST /admin/clear_chat`: Clear chat history (admin)
- `POST /admin/delete_room`: Delete a room completely

### Authentication

- `POST /auth/token`: Get authentication token
- `POST /auth/verify_token`: Verify token validity

## 💡 Usage Examples

### Creating a Profile

1. Enter a unique User ID
2. Set your Display Name
3. Upload an avatar image (optional, max 2MB)
4. Click "Next"

### Creating/Joining a Room

1. Enter a 5-digit Room ID
2. Set a secure password (min 8 characters)
3. Click "Start Chatting"

### Sending Messages

- Type your message in the input box
- Click the paper plane icon or press Enter
- For media messages, click the image icon and select a file

### Using Read Receipts

- Blue dot (🔵): Message has been read
- Empty circle (⚪): Message has not been read yet
- Messages you send show how many people have read them

## 🔧 Configuration Options

Key settings in `config.py`:

```python
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_hex(32))
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())

MAX_API_REQUESTS_PER_MINUTE = 60
MAX_ROOM_CREATION_PER_HOUR = 10
MAX_FILE_SIZE_MB = 5
PASSWORD_MIN_LENGTH = 8
ROOM_ID_LENGTH = 5
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Socket.IO](https://socket.io/) - Real-time communication
- [Fernet](https://cryptography.io/en/latest/fernet/) - Symmetric encryption
- [PyJWT](https://pyjwt.readthedocs.io/) - JSON Web Tokens
