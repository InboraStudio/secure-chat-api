from flask import Blueprint, request, jsonify
from utils.helpers import get_client_ip, validate_room_id
from utils.middleware import rate_limit
import config
import traceback

room_bp = Blueprint('room', __name__)

@room_bp.route('/create', methods=['POST'])
@rate_limit(max_requests=10, time_window=60)  # Limit to 10 room creations per minute
def create_room():
    try:
        # Get data from request
        data = request.get_json()
        print(f"Received request data: {data}")  # Debug log
        room_id = data.get('room_id')
        password = data.get('password')
        
        print(f"Room ID: {room_id} (type: {type(room_id)})")  # Debug log
        print(f"Password: {'*' * len(password) if password else None} (type: {type(password)})")  # Debug log
        
        # Validate inputs
        if not room_id or not password:
            print("Validation failed: Missing room_id or password")  # Debug log
            return jsonify({"success": False, "error": "Room ID and password are required"}), 400
        
        if not isinstance(room_id, str) or not isinstance(password, str):
            print(f"Validation failed: Invalid types - room_id: {type(room_id)}, password: {type(password)}")  # Debug log
            return jsonify({"success": False, "error": "Room ID and password must be strings"}), 400
        
        # Validate room ID format (must be 5 digits)
        if not validate_room_id(room_id):
            print(f"Validation failed: Invalid room ID format: {room_id}")  # Debug log
            return jsonify({"success": False, "error": "Room ID must be a 5-digit number"}), 400
            
        # Validate password length
        if len(password) < 8:
            print(f"Validation failed: Password too short ({len(password)} chars)")  # Debug log
            return jsonify({"success": False, "error": "Password must be at least 8 characters long"}), 400
            
        # Store the room with password
        config.room_passwords[room_id] = password
        
        # Initialize room data structures if they don't exist
        if room_id not in config.room_verified_ips:
            config.room_verified_ips[room_id] = []
            
        if room_id not in config.chat_rooms:
            config.chat_rooms[room_id] = []
            
        if room_id not in config.message_reactions:
            config.message_reactions[room_id] = {}
            
        if room_id not in config.typing_users:
            config.typing_users[room_id] = []
            
        if room_id not in config.room_files:
            config.room_files[room_id] = []
        
        # Add creator's IP to verified IPs
        client_ip = get_client_ip()
        if client_ip not in config.room_verified_ips[room_id]:
            config.room_verified_ips[room_id].append(client_ip)
        
        return jsonify({"success": True, "message": f"Room {room_id} created successfully!"})
    except Exception as e:
        print(f"Error creating room: {e}")
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500

@room_bp.route('/<room_id>/verify_ip', methods=['POST'])
def verify_ip(room_id):
    data = request.get_json()
    password = data.get("password")
    user_ip = data.get("ip")

    if config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Invalid password!"}), 401

    if room_id not in config.room_verified_ips:
        config.room_verified_ips[room_id] = []

    config.room_verified_ips[room_id].append(user_ip)

    return jsonify({"success": True, "message": f"IP {user_ip} verified for room {room_id}!"}) 