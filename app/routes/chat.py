from flask import Blueprint, render_template, jsonify, request
from app.utils.helpers import verify_token
from app.socket_events.chat import chat_rooms

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def home():
    return render_template('index.html')

@chat_bp.route('/room/create', methods=['POST'])
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

@chat_bp.route('/chat/<room_id>/messages', methods=['GET'])
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

@chat_bp.route('/chat/<room_id>/clear', methods=['POST'])
def clear_messages(room_id):
    if room_id in chat_rooms:
        chat_rooms[room_id] = []
        return jsonify({"success": True, "message": "Messages cleared successfully!"})
    return jsonify({"error": "Room not found!"}), 404

@chat_bp.route('/chat/<room_id>/verify', methods=['POST'])
def verify_room(room_id):
    if request.content_type == "application/json":
        data = request.get_json()
        password = data.get("password")
    else:
        password = request.form.get("password")

    if room_id not in room_passwords:
        return jsonify({"error": "Room not found!"}), 404

    if room_passwords[room_id] != password:
        return jsonify({"error": "Invalid password!"}), 401

    client_ip = get_client_ip()
    if room_id not in room_verified_ips:
        room_verified_ips[room_id] = []
    room_verified_ips[room_id].append(client_ip)

    token = generate_token(room_id)
    return jsonify({"token": token}) 