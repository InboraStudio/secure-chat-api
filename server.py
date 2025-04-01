from flask import Flask, request, jsonify, render_template, send_file
from flask_socketio import SocketIO, emit, join_room, leave_room
import jwt
import datetime
import os
import base64
from io import BytesIO
from PIL import Image
from cryptography.fernet import Fernet
import json
import time
import socket

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")
ENCRYPTION_KEY = Fernet.generate_key()
fernet = Fernet(ENCRYPTION_KEY)

chat_rooms = {}
room_passwords = {}
room_verified_ips = {}
user_profiles = {}
online_users = {}
message_reactions = {}
typing_users = {}
user_socket_map = {}

def generate_token(room_id):
    payload = {
        "room_id": room_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/room/create', methods=['POST'])
def create_room():
    if request.content_type == "application/json":
        data = request.get_json()
        room_id = data.get("room_id")
        password = data.get("password")
    else:
        room_id = request.form.get("room_id")
        password = request.form.get("password")

    if not room_id or not password:
        return jsonify({"error": "Room ID and password are required!"}), 400

    room_passwords[room_id] = password
    room_verified_ips[room_id] = []
    chat_rooms[room_id] = []
    message_reactions[room_id] = {}
    typing_users[room_id] = set()

    return jsonify({"success": True, "message": f"Room {room_id} created successfully!"})

@app.route('/user/profile', methods=['POST'])
def create_profile():
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username")
    avatar = data.get("avatar")

    if not user_id or not username:
        return jsonify({"error": "User ID and username are required!"}), 400

    user_profiles[user_id] = {
        "username": username,
        "avatar": avatar,
        "created_at": time.time()
    }

    return jsonify({"success": True, "message": "Profile created successfully!"})

@app.route('/user/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    if user_id in user_profiles:
        return jsonify(user_profiles[user_id])
    return jsonify({"error": "Profile not found!"}), 404

@socketio.on('join')
def on_join(data):
    room = data['room']
    user_id = data['user_id']
    
    user_socket_map[user_id] = request.sid
    
    if room not in chat_rooms:
        chat_rooms[room] = []
    if room not in online_users:
        online_users[room] = set()
    if room not in message_reactions:
        message_reactions[room] = {}
    if room not in typing_users:
        typing_users[room] = set()
    
    join_room(room)
    online_users[room].add(user_id)
    
    emit('online_count', {
        'room': room,
        'count': len(online_users[room])
    }, room=room, broadcast=True)
    
    emit('status', {
        'msg': f'👋 {user_id} has joined the room'
    }, room=room, broadcast=True)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    user_id = data['user_id']
    
    if room in online_users:
        online_users[room].discard(user_id)
        if user_id in typing_users.get(room, set()):
            typing_users[room].discard(user_id)
        
        emit('online_count', {
            'room': room,
            'count': len(online_users[room])
        }, room=room, broadcast=True)
        
        emit('status', {
            'msg': f'👋 {user_id} has left the room'
        }, room=room, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = None
    for uid, sid in user_socket_map.items():
        if sid == request.sid:
            user_id = uid
            break
    
    if user_id:
        for room in list(online_users.keys()):
            if user_id in online_users[room]:
                online_users[room].discard(user_id)
                if user_id in typing_users.get(room, set()):
                    typing_users[room].discard(user_id)
                
                emit('online_count', {
                    'room': room,
                    'count': len(online_users[room])
                }, room=room, broadcast=True)
                
                emit('status', {
                    'msg': f'👋 {user_id} has disconnected'
                }, room=room, broadcast=True)
        
        del user_socket_map[user_id]

@socketio.on('message')
def handle_message(data):
    room = data['room']
    user_id = data['user_id']
    message = data['message']
    
    if room not in chat_rooms:
        chat_rooms[room] = []
    
    timestamp = int(time.time() * 1000)
    current_time = datetime.datetime.now()
    formatted_date = current_time.strftime("%Y-%m-%d")
    formatted_time = current_time.strftime("%I:%M %p")
    
    message_data = {
        'user_id': user_id,
        'message': message,
        'timestamp': timestamp,
        'date': formatted_date,
        'time': formatted_time,
        'is_sent': True
    }
    
    chat_rooms[room].append(message_data)
    
    if len(chat_rooms[room]) > 100:
        chat_rooms[room] = chat_rooms[room][-100:]
    
    emit('message', message_data, room=room, broadcast=True)

@socketio.on('typing')
def handle_typing(data):
    room = data['room']
    user_id = data['user_id']
    is_typing = data['is_typing']
    
    if room not in typing_users:
        typing_users[room] = set()
    
    if is_typing:
        typing_users[room].add(user_id)
    else:
        typing_users[room].discard(user_id)
    
    emit('typing_status', {
        'typing_users': list(typing_users[room])
    }, room=room)

@socketio.on('reaction')
def handle_reaction(data):
    room = data['room']
    message_id = data['message_id']
    user_id = data['user_id']
    reaction = data['reaction']

    if room in message_reactions and message_id in message_reactions[room]:
        if reaction not in message_reactions[room][message_id]:
            message_reactions[room][message_id][reaction] = set()
        message_reactions[room][message_id][reaction].add(user_id)
        
        emit('reaction_update', {
            'message_id': message_id,
            'reactions': {
                r: list(users) for r, users in message_reactions[room][message_id].items()
            }
        }, room=room)

@app.route('/chat/<room_id>/messages', methods=['GET'])
def get_messages(room_id):
    if room_id not in chat_rooms:
        chat_rooms[room_id] = []
    
    user_id = request.args.get('user_id')
    
    messages = []
    for msg in chat_rooms[room_id]:
        msg_copy = msg.copy()
        msg_copy['is_sent'] = msg_copy['user_id'] == user_id
        messages.append(msg_copy)
    
    return jsonify(messages)

@app.route('/chat/<room_id>/clear', methods=['POST'])
def clear_chat(room_id):
    if room_id in chat_rooms:
        chat_rooms[room_id] = []
        message_reactions[room_id] = {}
    return jsonify({"success": True, "message": "Chat cleared!"})

@app.route('/room/<room_id>/verify_ip', methods=['POST'])
def verify_ip(room_id):
    data = request.get_json()
    password = data.get("password")
    user_ip = data.get("ip")

    if room_passwords.get(room_id) != password:
        return jsonify({"error": "Invalid password!"}), 401

    if room_id not in room_verified_ips:
        room_verified_ips[room_id] = []

    room_verified_ips[room_id].append(user_ip)

    return jsonify({"success": True, "message": f"IP {user_ip} verified for room {room_id}!"})

@app.route('/chat/<room_id>', methods=['POST'])
def send_message(room_id):
    client_ip = get_client_ip()
    data = request.get_json()
    message = data.get("message")
    password = data.get("password")

    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401

    if room_id not in chat_rooms:
        chat_rooms[room_id] = []

    chat_rooms[room_id].append(f"[{client_ip}] {message}")
    return jsonify({"success": True, "message": "Message sent securely!"})

@app.route('/chat/<room_id>/web', methods=['GET'])
def chat_web(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")

    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return "<h3>Access Denied! Verify your IP or provide the correct password.</h3>", 401

    messages = chat_rooms.get(room_id, [])
    return render_template("chat.html", room_id=room_id, messages=messages)

@app.route('/admin')
def admin_panel():
    return render_template("admin.html")

@app.route('/admin/verify_ip', methods=['POST'])
def admin_verify_ip():
    room_id = request.form.get("room_id")
    ip = request.form.get("ip")
    password = request.form.get("password")

    if not room_id or not ip or not password:
        return jsonify({"error": "All fields are required!"}), 400

    if room_passwords.get(room_id) != password:
        return jsonify({"error": "Unauthorized access!"}), 401

    if room_id not in room_verified_ips:
        room_verified_ips[room_id] = []
    
    room_verified_ips[room_id].append(ip)
    return jsonify({"success": True, "message": f"IP {ip} verified for room {room_id}!"})

@app.route('/admin/clear_chat', methods=['POST'])
def admin_clear_chat():
    room_id = request.form.get("room_id")
    password = request.form.get("password")

    if room_passwords.get(room_id) != password:
        return jsonify({"error": "Unauthorized access!"}), 401

    if room_id in chat_rooms:
        chat_rooms[room_id] = []
    return jsonify({"success": True, "message": "Chat cleared successfully!"})

@app.route('/admin/delete_room', methods=['POST'])
def admin_delete_room():
    room_id = request.form.get("room_id")
    password = request.form.get("password")

    if room_passwords.get(room_id) != password:
        return jsonify({"error": "Unauthorized access!"}), 401

    chat_rooms.pop(room_id, None)
    room_verified_ips.pop(room_id, None)
    room_passwords.pop(room_id, None)
    return jsonify({"success": True, "message": f"Room {room_id} deleted!"})

if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\nServer is running!")
    print(f"Local IP: {local_ip}")
    print(f"Access the chat at: http://{local_ip}:10000")
    print("\nPress Ctrl+C to stop the server.\n")
    
    socketio.run(app, host='0.0.0.0', port=10000, debug=True)
