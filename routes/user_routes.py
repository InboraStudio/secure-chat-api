from flask import Blueprint, request, jsonify
import time
import config

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['POST'])
def create_profile():
    data = request.get_json()
    user_id = data.get("user_id")
    username = data.get("username")
    avatar = data.get("avatar")
    status_message = data.get("status_message", "")  # Added status message
    theme = data.get("theme", "light")  # Added theme preference

    if not user_id or not username:
        return jsonify({"error": "User ID and username are required!"}), 400

    config.user_profiles[user_id] = {
        "username": username,
        "avatar": avatar,
        "status_message": status_message,
        "theme": theme,
        "created_at": time.time(),
        "last_active": time.time()
    }

    return jsonify({"success": True, "message": "Profile created successfully!"})

@user_bp.route('/profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    if user_id in config.user_profiles:
        return jsonify(config.user_profiles[user_id])
    return jsonify({"error": "Profile not found!"}), 404

@user_bp.route('/profile/<user_id>', methods=['PUT'])
def update_profile(user_id):
    if user_id not in config.user_profiles:
        return jsonify({"error": "Profile not found!"}), 404
    
    data = request.get_json()
    
    if "username" in data:
        config.user_profiles[user_id]["username"] = data["username"]
    if "avatar" in data:
        config.user_profiles[user_id]["avatar"] = data["avatar"]
    if "status_message" in data:
        config.user_profiles[user_id]["status_message"] = data["status_message"]
    if "theme" in data:
        config.user_profiles[user_id]["theme"] = data["theme"]
    
    config.user_profiles[user_id]["last_active"] = time.time()
    
    return jsonify({"success": True, "message": "Profile updated successfully!"})

@user_bp.route('/presence/<user_id>', methods=['POST'])
def update_presence(user_id):
    if user_id not in config.user_profiles:
        return jsonify({"error": "User not found"}), 404
    
    # Update the last active timestamp
    config.user_profiles[user_id]["last_active"] = time.time()
    
    data = request.get_json()
    status = data.get("status", "online")  # online, away, busy, offline
    
    if "status" in data:
        config.user_profiles[user_id]["status"] = status
        
    return jsonify({"success": True, "user_id": user_id, "status": status})

@user_bp.route('/presence', methods=['GET'])
def get_all_presence():
    room_id = request.args.get("room_id")
    
    if not room_id or room_id not in config.online_users:
        return jsonify({"error": "Room not found or no users online"}), 404
    
    # Get online status of all users in the room
    users_status = {}
    for user_id in config.online_users[room_id]:
        if user_id in config.user_profiles:
            last_active = config.user_profiles[user_id].get("last_active", 0)
            status = config.user_profiles[user_id].get("status", "offline")
            
            # If user hasn't been active in the last 5 minutes, mark as away
            if time.time() - last_active > 300 and status == "online":
                status = "away"
                
            users_status[user_id] = {
                "status": status,
                "last_active": last_active,
                "username": config.user_profiles[user_id].get("username", "Unknown"),
                "avatar": config.user_profiles[user_id].get("avatar", "")
            }
    
    return jsonify({
        "room_id": room_id,
        "online_count": len(config.online_users[room_id]),
        "users": users_status
    }) 