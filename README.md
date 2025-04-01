# 🔐 Secure Chat API

<div align="center">
  <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Socket.io-010101?style=for-the-badge&logo=socket.io&logoColor=white" alt="Socket.io"/>
  <img src="https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white" alt="JWT"/>
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License"/>
</div>

<p align="center">A secure, end-to-end encrypted chat application with room-based messaging, real-time notifications, and robust authentication.</p>

<div align="center">
  <a href="#key-features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#getting-started">Getting Started</a> •
  <a href="#api-documentation">API Docs</a> •
  <a href="#security">Security</a> •
  <a href="#deployment">Deployment</a>
</div>

---

## 📝 Overview

Secure Chat API is a modern, real-time messaging platform designed with security and privacy as core principles. It enables users to create private chat rooms, exchange end-to-end encrypted messages, and manage access through various authentication methods.

## ✨ Key Features

- **Real-time Messaging** - Instant message delivery using Socket.IO
- **End-to-End Encryption** - All messages are encrypted using Fernet symmetric encryption
- **Room-Based Conversations** - Create and join password-protected chat rooms
- **User Presence Detection** - See when users join, leave, or are typing
- **Message Reactions** - React to messages with emojis
- **Multiple Access Controls**:
  - JWT token authentication
  - Password protection
  - IP-based verification
- **Admin Dashboard** - Manage rooms, users, and messages
- **Responsive Web Interface** - Access chats from any device
- **REST API & WebSocket Support** - Flexible integration options

## 🛠️ Tech Stack

- **Backend**: Flask, Flask-SocketIO, Python 3.x
- **Security**: JWT, Cryptography, Fernet encryption
- **Real-time Communication**: Socket.IO
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Docker-ready, deployable to any cloud platform

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/secure-chat-api.git
cd secure-chat-api
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Run the server**

```bash
python server.py
```

4. **Access the application**

- Open your browser and navigate to: `http://127.0.0.1:10000`
- The server console will display your local IP for LAN access

### Project Structure

```
/secure-chat-api
│── /app                      # Application modules
│   ├── /config               # Configuration settings
│   ├── /routes               # API route handlers
│   ├── /socket_events        # Socket.IO event handlers
│   ├── /utils                # Utility functions
│   └── __init__.py           # App initialization
│── /templates                # HTML templates
│   └── index.html            # Main chat interface
│── .gitignore                # Git ignore file
│── requirements.txt          # Project dependencies
│── server.py                 # Main server file
│── README.md                 # Project documentation
```

## 📚 API Documentation

### Authentication

All API endpoints require either:
- A valid JWT token in the Authorization header
- Room password for specific room operations
- Verified IP address (for previously approved clients)

### REST Endpoints

#### Chat Room Management

```bash
# Create a new chat room
POST /room/create
{
  "room_id": "unique_room_id",
  "password": "room_password"
}

# Verify room access
POST /chat/{room_id}/verify
{
  "password": "room_password"
}
```

#### Messaging

```bash
# Send a message to a room
POST /chat/{room_id}
{
  "message": "Your message",
  "password": "room_password"
}

# Get messages from a room
GET /chat/{room_id}/messages?user_id={user_id}

# Clear chat history
POST /chat/{room_id}/clear
{
  "password": "room_password"
}
```

#### User Profiles

```bash
# Create a user profile
POST /user/profile
{
  "user_id": "unique_user_id",
  "username": "display_name",
  "avatar": "avatar_url"
}

# Get a user profile
GET /user/profile/{user_id}
```

#### Admin Operations

```bash
# Verify a user's IP
POST /admin/verify_ip
{
  "room_id": "room_id",
  "ip": "ip_address",
  "password": "room_password"
}

# Delete a chat room
POST /admin/delete_room
{
  "room_id": "room_id",
  "password": "room_password"
}
```

### WebSocket Events

```javascript
// Join a room
socket.emit('join', {room: 'room_id', user_id: 'user_id'});

// Send a message
socket.emit('message', {room: 'room_id', user_id: 'user_id', message: 'message'});

// Typing indicator
socket.emit('typing', {room: 'room_id', user_id: 'user_id', is_typing: true});

// Leave a room
socket.emit('leave', {room: 'room_id', user_id: 'user_id'});

// React to a message
socket.emit('reaction', {room: 'room_id', message_id: 'message_id', user_id: 'user_id', reaction: '👍'});
```

## 🔒 Security

Secure Chat API implements multiple layers of security:

1. **Authentication**
   - JWT tokens with expiration
   - Room password protection
   - IP-based verification

2. **Encryption**
   - End-to-end encryption using Fernet symmetric algorithm
   - Secure key management

3. **Access Control**
   - Role-based permissions
   - Room creator has admin privileges
   - Verification required for new IPs

4. **Data Protection**
   - Messages stored in encrypted format
   - Option to clear chat history
   - Automatic message pruning (configurable message limit)

## 📦 Deployment

### Local Deployment

Run the server on your local machine:

```bash
python server.py
```

### Cloud Deployment

The application is ready to deploy on various cloud platforms:

#### Render.com

1. Push your code to GitHub
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Configure:
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python server.py`

#### Docker Deployment

```bash
# Build Docker image
docker build -t secure-chat-api .

# Run container
docker run -p 10000:10000 secure-chat-api
```

## 🌟 Future Improvements

- [ ] Persistent storage with database integration
- [ ] File sharing capabilities
- [ ] Voice and video chat integration
- [ ] Multi-factor authentication
- [ ] Message search functionality
- [ ] Push notifications
- [ ] Mobile application

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- Initial development by [Your Name](https://github.com/yourusername)

---

<div align="center">
  <p>Made with ❤️ for secure communications</p>
  <p>© 2023 Secure Chat API</p>
</div>
