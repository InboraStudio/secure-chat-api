from flask import Blueprint, request, jsonify
from utils.helpers import get_client_ip, generate_token, verify_token
import config
import time

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/token', methods=['POST'])
def get_token():
    """Generate an authentication token for API access"""
    data = request.get_json()
    
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400
        
    room_id = data.get('room_id')
    password = data.get('password')
    
    if not room_id or not password:
        return jsonify({"success": False, "error": "Room ID and password are required"}), 400
        
   
    if room_id not in config.room_passwords or config.room_passwords[room_id] != password:
        return jsonify({"success": False, "error": "Invalid room ID or password"}), 401
    
    
    client_ip = get_client_ip()
    if room_id not in config.room_verified_ips:
        config.room_verified_ips[room_id] = []
        
    if client_ip not in config.room_verified_ips[room_id]:
        config.room_verified_ips[room_id].append(client_ip)
    
   
    token = generate_token(room_id)
    
    return jsonify({
        "success": True, 
        "token": token, 
        "expires_in": 3600  
    })
    
@auth_bp.route('/verify_token', methods=['POST'])
def verify_token_route():
    """Verify an authentication token is valid"""
    data = request.get_json()
    
    if not data or 'token' not in data:
        return jsonify({"success": False, "error": "Token is required"}), 400
        
    token = data['token']
    room_id = verify_token(token)
    
    if not room_id:
        return jsonify({"success": False, "error": "Invalid or expired token"}), 401
        
    return jsonify({
        "success": True,
        "room_id": room_id
    }) 