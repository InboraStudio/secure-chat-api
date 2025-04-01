from flask import Blueprint, request, jsonify, render_template
import os
import config
from utils.middleware import token_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def admin_panel():
    return render_template("admin.html")

@admin_bp.route('/verify_ip', methods=['POST'])
@token_required
def admin_verify_ip():
    data = request.get_json() or {}
    room_id = data.get("room_id")
    ip = data.get("ip")
    password = data.get("password")

    if not room_id or not ip or not password:
        return jsonify({"success": False, "error": "All fields are required!"}), 400

    if hasattr(request, 'is_authenticated') and request.is_authenticated and request.authenticated_room == room_id:
        pass
    elif config.room_passwords.get(room_id) != password:
        return jsonify({"success": False, "error": "Unauthorized access!"}), 401

    if room_id not in config.room_verified_ips:
        config.room_verified_ips[room_id] = []
    
    if ip not in config.room_verified_ips[room_id]:
        config.room_verified_ips[room_id].append(ip)
        
    return jsonify({"success": True, "message": f"IP {ip} verified for room {room_id}!"})

@admin_bp.route('/clear_chat', methods=['POST'])
@token_required
def admin_clear_chat():
    data = request.get_json() or {}
    room_id = data.get("room_id")
    password = data.get("password")

    if not room_id or not password:
        return jsonify({"success": False, "error": "Room ID and password are required!"}), 400

    if hasattr(request, 'is_authenticated') and request.is_authenticated and request.authenticated_room == room_id:
        pass
    elif config.room_passwords.get(room_id) != password:
        return jsonify({"success": False, "error": "Unauthorized access!"}), 401

    if room_id in config.chat_rooms:
        config.chat_rooms[room_id] = []
        if room_id in config.message_reactions:
            config.message_reactions[room_id] = {}
            
    return jsonify({"success": True, "message": "Chat cleared successfully!"})

@admin_bp.route('/delete_room', methods=['POST'])
@token_required
def admin_delete_room():
    data = request.get_json() or {}
    room_id = data.get("room_id")
    password = data.get("password")

    if not room_id or not password:
        return jsonify({"success": False, "error": "Room ID and password are required!"}), 400

    if hasattr(request, 'is_authenticated') and request.is_authenticated and request.authenticated_room == room_id:
        pass
    elif config.room_passwords.get(room_id) != password:
        return jsonify({"success": False, "error": "Unauthorized access!"}), 401

    config.chat_rooms.pop(room_id, None)
    config.room_verified_ips.pop(room_id, None)
    config.room_passwords.pop(room_id, None)
    config.message_reactions.pop(room_id, None)
    config.typing_users.pop(room_id, None)
    
    if room_id in config.room_files:
        room_dir = os.path.join(config.UPLOAD_FOLDER, room_id)
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
        config.room_files.pop(room_id, None)
    
    return jsonify({"success": True, "message": f"Room {room_id} deleted!"}) 