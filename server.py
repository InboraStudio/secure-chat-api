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
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=50 * 1024 * 1024)  # 50MB buffer for media

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
room_files = {}  # To store file information per room

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    room_files[room_id] = []  # Initialize files list for the room

    return jsonify({"success": True, "message": f"Room {room_id} created successfully!"})

@app.route('/user/profile', methods=['POST'])
def create_profile():
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username")
    avatar = data.get("avatar")
    status_message = data.get("status_message", "")  # Added status message
    theme = data.get("theme", "light")  # Added theme preference

    if not user_id or not username:
        return jsonify({"error": "User ID and username are required!"}), 400

    user_profiles[user_id] = {
        "username": username,
        "avatar": avatar,
        "status_message": status_message,
        "theme": theme,
        "created_at": time.time(),
        "last_active": time.time()
    }

    return jsonify({"success": True, "message": "Profile created successfully!"})

@app.route('/user/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    if user_id in user_profiles:
        return jsonify(user_profiles[user_id])
    return jsonify({"error": "Profile not found!"}), 404

@app.route('/user/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    if user_id not in user_profiles:
        return jsonify({"error": "Profile not found!"}), 404
    
    data = request.get_json()
    
    if "username" in data:
        user_profiles[user_id]["username"] = data["username"]
    if "avatar" in data:
        user_profiles[user_id]["avatar"] = data["avatar"]
    if "status_message" in data:
        user_profiles[user_id]["status_message"] = data["status_message"]
    if "theme" in data:
        user_profiles[user_id]["theme"] = data["theme"]
    
    user_profiles[user_id]["last_active"] = time.time()
    
    return jsonify({"success": True, "message": "Profile updated successfully!"})

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
    if room not in room_files:
        room_files[room] = []
    
    join_room(room)
    online_users[room].add(user_id)
    
    emit('online_count', {
        'room': room,
        'count': len(online_users[room])
    }, room=room, broadcast=True)
    
    emit('status', {
        'msg': f'👋 {user_id} has joined the room'
    }, room=room, broadcast=True)
    
    # Send list of files in the room
    emit('files_list', {
        'room': room,
        'files': room_files[room]
    }, room=request.sid)

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
    media = data.get('media', None)
    
    if room not in chat_rooms:
        chat_rooms[room] = []
    
    # Get user info
    username = user_profiles.get(user_id, {}).get('username', user_id)
    
    now = datetime.datetime.now()
    formatted_date = now.strftime("%B %d, %Y")
    formatted_time = now.strftime("%I:%M %p")
    
    message_id = f"msg_{int(time.time() * 1000)}"
    
    message_data = {
        "id": message_id,
        "user_id": user_id,
        "username": username,
        "message": message,
        "timestamp": int(time.time() * 1000),
        "date": formatted_date,
        "time": formatted_time
    }
    
    # Add media data if present
    has_media = False
    if media:
        try:
            print(f"Received media message from {user_id}: {media['type']}, size: {len(media['data'])}")
            message_data["media"] = {
                "type": media["type"],
                "data": media["data"],
                "name": media["name"]
            }
            has_media = True
        except Exception as e:
            print(f"Error processing media: {str(e)}")
            return {"status": "error", "message": f"Failed to process media: {str(e)}"}
    
    chat_rooms[room].append(message_data)
    
    # Verify media data is in the message before sending
    if has_media:
        print(f"Sending media message to room {room}: {message_data['media']['type']}")
    
    emit('message', message_data, room=room, broadcast=True)
    
    # Send acknowledgment back to the sender
    return {"status": "success", "message_id": message_id}

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
        'room': room,
        'typing_users': list(typing_users[room])
    }, room=room)

@socketio.on('reaction')
def handle_reaction(data):
    room = data['room']
    message_id = data['message_id']
    user_id = data['user_id']
    reaction = data['reaction']

    if room not in message_reactions:
        message_reactions[room] = {}
    
    if message_id not in message_reactions[room]:
        message_reactions[room][message_id] = {}
        
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
    client_ip = get_client_ip()
    password = request.args.get("password")
    search_query = request.args.get("search")
    
    if room_id not in chat_rooms:
        return jsonify({"error": "Room not found!"}), 404
    
    # If password provided, verify it
    if password and password == room_passwords.get(room_id):
        room_verified_ips[room_id].append(client_ip)
        
    if client_ip not in room_verified_ips.get(room_id, []):
        return jsonify({"error": "Access denied!"}), 403
    
    messages = chat_rooms[room_id]
    
    # If search query is provided, filter messages
    if search_query:
        messages = [msg for msg in messages if search_query.lower() in msg.get('message', '').lower()]
    
    # Format messages to include username and ensure media is included
    formatted_messages = []
    for msg in messages:
        message_copy = msg.copy()
        user_id = msg.get("user_id")
        if user_id in user_profiles:
            message_copy["username"] = user_profiles[user_id].get("username", user_id)
            message_copy["avatar"] = user_profiles[user_id].get("avatar", "")
        formatted_messages.append(message_copy)
    
    return jsonify({
        "success": True,
        "messages": formatted_messages,
        "count": len(formatted_messages)
    })

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

# File upload route
@app.route('/chat/<room_id>/upload', methods=['POST'])
def upload_file(room_id):
    client_ip = get_client_ip()
    password = request.form.get("password")
    
    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and allowed_file(file.filename):
        # Create room directory if it doesn't exist
        room_dir = os.path.join(UPLOAD_FOLDER, room_id)
        os.makedirs(room_dir, exist_ok=True)
        
        # Generate a secure filename
        filename = f"{int(time.time())}_{file.filename}"
        filepath = os.path.join(room_dir, filename)
        
        # Save the file
        file.save(filepath)
        
        # Add file info to room_files
        file_info = {
            'id': f"file_{int(time.time())}",
            'filename': file.filename,
            'stored_filename': filename,
            'path': filepath,
            'size': os.path.getsize(filepath),
            'type': file.content_type,
            'uploaded_by': user_id,
            'uploaded_at': int(time.time() * 1000)
        }
        
        if room_id not in room_files:
            room_files[room_id] = []
            
        room_files[room_id].append(file_info)
        
        # Notify all users in the room about the new file
        socketio.emit('file_uploaded', file_info, room=room_id)
        
        return jsonify({
            "success": True, 
            "message": "File uploaded successfully!", 
            "file": file_info
        })
    
    return jsonify({"error": "File type not allowed"}), 400

# File download route
@app.route('/chat/<room_id>/files/<filename>', methods=['GET'])
def download_file(room_id, filename):
    client_ip = get_client_ip()
    password = request.args.get("password")
    
    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    # Find the file in room_files
    file_info = None
    if room_id in room_files:
        for file in room_files[room_id]:
            if file['stored_filename'] == filename:
                file_info = file
                break
    
    if not file_info:
        return jsonify({"error": "File not found"}), 404
    
    # Return the file
    return send_file(file_info['path'], as_attachment=True, download_name=file_info['filename'])

# List files in a room
@app.route('/chat/<room_id>/files', methods=['GET'])
def list_files(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")
    
    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if room_id not in room_files:
        return jsonify([])
    
    return jsonify(room_files[room_id])

# Delete a file
@app.route('/chat/<room_id>/files/<filename>', methods=['DELETE'])
def delete_file(room_id, filename):
    client_ip = get_client_ip()
    password = request.args.get("password")
    
    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    # Find the file in room_files
    file_info = None
    file_index = -1
    if room_id in room_files:
        for i, file in enumerate(room_files[room_id]):
            if file['stored_filename'] == filename:
                file_info = file
                file_index = i
                break
    
    if not file_info:
        return jsonify({"error": "File not found"}), 404
    
    # Delete the file from storage
    try:
        os.remove(file_info['path'])
        # Remove from room_files
        if file_index != -1:
            room_files[room_id].pop(file_index)
        
        # Notify all users in the room about file deletion
        socketio.emit('file_deleted', {"filename": filename}, room=room_id)
        
        return jsonify({"success": True, "message": "File deleted successfully!"})
    except Exception as e:
        return jsonify({"error": f"Error deleting file: {str(e)}"}), 500

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
    
    # Also clean up files
    if room_id in room_files:
        # Delete all files in the room directory
        room_dir = os.path.join(UPLOAD_FOLDER, room_id)
        if os.path.exists(room_dir):
            for file in os.listdir(room_dir):
                try:
                    os.remove(os.path.join(room_dir, file))
                except:
                    pass
            try:
                os.rmdir(room_dir)
            except:
                pass
        room_files.pop(room_id, None)
    
    return jsonify({"success": True, "message": f"Room {room_id} deleted!"})

@app.route('/chat/<room_id>/search', methods=['GET'])
def search_messages(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")
    query = request.args.get("query", "").lower()
    
    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    if room_id not in chat_rooms:
        return jsonify([])
    
    # Search through messages
    results = []
    for msg in chat_rooms[room_id]:
        if 'message' in msg and query in msg['message'].lower():
            results.append(msg)
    
    return jsonify({
        "success": True,
        "query": query,
        "results": results,
        "result_count": len(results)
    })

@app.route('/user/presence/<user_id>', methods=['POST'])
def update_presence(user_id):
    if user_id not in user_profiles:
        return jsonify({"error": "User not found"}), 404
    
    # Update the last active timestamp
    user_profiles[user_id]["last_active"] = time.time()
    
    data = request.get_json()
    status = data.get("status", "online")  # online, away, busy, offline
    
    if "status" in data:
        user_profiles[user_id]["status"] = status
        
    return jsonify({"success": True, "user_id": user_id, "status": status})

@app.route('/user/presence', methods=['GET'])
def get_all_presence():
    room_id = request.args.get("room_id")
    
    if not room_id or room_id not in online_users:
        return jsonify({"error": "Room not found or no users online"}), 404
    
    # Get online status of all users in the room
    users_status = {}
    for user_id in online_users[room_id]:
        if user_id in user_profiles:
            last_active = user_profiles[user_id].get("last_active", 0)
            status = user_profiles[user_id].get("status", "offline")
            
            # If user hasn't been active in the last 5 minutes, mark as away
            if time.time() - last_active > 300 and status == "online":
                status = "away"
                
            users_status[user_id] = {
                "status": status,
                "last_active": last_active,
                "username": user_profiles[user_id].get("username", "Unknown"),
                "avatar": user_profiles[user_id].get("avatar", "")
            }
    
    return jsonify({
        "room_id": room_id,
        "online_count": len(online_users[room_id]),
        "users": users_status
    })

@app.route('/chat/<room_id>/messages/<message_id>', methods=['DELETE'])
def delete_message(room_id, message_id):
    client_ip = get_client_ip()
    password = request.args.get("password")
    user_id = request.args.get("user_id")
    
    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if room_id not in chat_rooms:
        return jsonify({"error": "Room not found"}), 404
    
    # Find the message
    message_index = -1
    message = None
    for i, msg in enumerate(chat_rooms[room_id]):
        if 'id' in msg and msg['id'] == message_id:
            message = msg
            message_index = i
            break
    
    if message_index == -1:
        return jsonify({"error": "Message not found"}), 404
    
    # Check if user is authorized to delete this message
    # Only the message sender or room admin (whoever has the password) can delete messages
    is_admin = room_passwords.get(room_id) == password
    is_sender = message.get('user_id') == user_id
    
    if not is_admin and not is_sender:
        return jsonify({"error": "Unauthorized to delete this message"}), 403
    
    # Remove the message
    removed_message = chat_rooms[room_id].pop(message_index)
    
    # Notify all users in the room about message deletion
    socketio.emit('message_deleted', {
        "message_id": message_id,
        "deleted_by": user_id,
        "is_admin_delete": is_admin and not is_sender
    }, room=room_id)
    
    return jsonify({
        "success": True, 
        "message": "Message deleted successfully!",
        "deleted_message": removed_message
    })

if __name__ == '__main__':
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\nServer is running!")
    print(f"Local IP: {local_ip}")
    print(f"Access the chat at: http://{local_ip}:10000")
    print("\nPress Ctrl+C to stop the server.\n")
    
    socketio.run(app, host='0.0.0.0', port=10000, debug=True)
