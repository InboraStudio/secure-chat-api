from flask import Blueprint, request, jsonify, send_file, render_template, current_app
import os
import time
from utils.helpers import get_client_ip, allowed_file, encrypt_message, decrypt_message
from utils.middleware import token_required
import config
from datetime import datetime

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/<room_id>/messages', methods=['GET'])
@token_required
def get_messages(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")
    user_id = request.args.get("user_id")
    mark_as_read = request.args.get("mark_as_read", "true").lower() in ["true", "1", "yes"]
    
    # Check if authenticated via token
    if hasattr(request, 'is_authenticated') and request.is_authenticated and request.authenticated_room == room_id:
        pass  # Allow access if authenticated via token
    # Otherwise check IP or password
    elif client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if room_id not in config.chat_rooms:
        return jsonify([])
    
    # Decrypt messages
    decrypted_messages = []
    updated_messages = []
    
    # Initialize read status tracking if needed
    if room_id not in config.message_read_status:
        config.message_read_status[room_id] = {}
    
    for i, encrypted_message in enumerate(config.chat_rooms[room_id]):
        message = decrypt_message(encrypted_message)
        
        # Add is_sent flag for UI
        if user_id:
            message['is_sent'] = message.get('user_id') == user_id
            
            # Add read status info
            message_id = message.get('id')
            if message_id:
                # Ensure read_by list exists
                if 'read_by' not in message:
                    message['read_by'] = []
                    
                # If requested, mark message as read by current user
                if mark_as_read and user_id and user_id not in message['read_by']:
                    message['read_by'].append(user_id)
                    updated_messages.append(message_id)
                    
                    # Update the message in the database
                    config.chat_rooms[room_id][i] = encrypt_message(message)
                    
                    # Update read status tracking
                    if message_id not in config.message_read_status[room_id]:
                        config.message_read_status[room_id][message_id] = {
                            'read_by': [user_id],
                            'timestamp': message.get('timestamp', int(time.time() * 1000))
                        }
                    else:
                        if user_id not in config.message_read_status[room_id][message_id]['read_by']:
                            config.message_read_status[room_id][message_id]['read_by'].append(user_id)
                
                # Add convenience properties for UI
                if message.get('user_id') == user_id:
                    # For sender: how many people have read this message
                    read_count = len(message.get('read_by', []))
                    message['read_count'] = read_count
                    message['is_read'] = read_count > 1  # More than just the sender
                else:
                    # For receiver: whether I have read this message
                    message['is_read'] = user_id in message.get('read_by', [])
        
        decrypted_messages.append(message)
    
    # Notify other users about read status change
    if updated_messages and hasattr(current_app, 'socketio'):
        current_app.socketio.emit('messages_read', {
            'room_id': room_id,
            'message_ids': updated_messages,
            'read_by': user_id
        }, room=room_id)
    
    return jsonify(decrypted_messages)

@chat_bp.route('/<room_id>/clear', methods=['POST'])
@token_required
def clear_chat(room_id):
    client_ip = get_client_ip()
    data = request.get_json()
    password = data.get("password", "")
    
    # Check if authenticated via token
    if hasattr(request, 'is_authenticated') and request.is_authenticated and request.authenticated_room == room_id:
        pass  # Allow access if authenticated via token
    # Otherwise check password
    elif config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Provide the correct password."}), 401
    
    if room_id in config.chat_rooms:
        config.chat_rooms[room_id] = []
        config.message_reactions[room_id] = {}
    return jsonify({"success": True, "message": "Chat cleared!"})

@chat_bp.route('/<room_id>', methods=['POST'])
@token_required
def send_message(room_id):
    client_ip = get_client_ip()
    data = request.get_json()
    message = data.get("message")
    password = data.get("password")
    user_id = data.get("user_id", "anonymous")

    # Check if authenticated via token
    if hasattr(request, 'is_authenticated') and request.is_authenticated and request.authenticated_room == room_id:
        pass  # Allow access if authenticated via token
    # Otherwise check IP or password
    elif client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401

    if room_id not in config.chat_rooms:
        config.chat_rooms[room_id] = []
    
    # Create message object
    timestamp = int(time.time() * 1000)
    message_id = str(timestamp)
    now = datetime.now()
    message_obj = {
        'id': message_id,
        'user_id': user_id,
        'client_ip': client_ip,
        'message': message,
        'timestamp': timestamp,
        'date': now.strftime("%Y-%m-%d"),
        'time': now.strftime("%I:%M %p"),
        'read_by': [user_id]  # Sender has automatically seen the message
    }
    
    # Initialize read status for this message
    if room_id not in config.message_read_status:
        config.message_read_status[room_id] = {}
    
    config.message_read_status[room_id][message_id] = {
        'read_by': [user_id],  # Sender has automatically seen the message
        'timestamp': timestamp
    }
    
    # Encrypt the message before storing
    encrypted_message = encrypt_message(message_obj)
    config.chat_rooms[room_id].append(encrypted_message)
    
    return jsonify({"success": True, "message": "Message sent securely!"})

@chat_bp.route('/<room_id>/web', methods=['GET'])
def chat_web(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")

    if client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return "<h3>Access Denied! Verify your IP or provide the correct password.</h3>", 401

    messages = config.chat_rooms.get(room_id, [])
    return render_template("chat.html", room_id=room_id, messages=messages)

@chat_bp.route('/<room_id>/upload', methods=['POST'])
def upload_file(room_id):
    client_ip = get_client_ip()
    password = request.form.get("password")
    
    if client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    user_id = request.form.get('user_id')
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    if file and allowed_file(file.filename):
        # Create room directory if it doesn't exist
        room_dir = os.path.join(config.UPLOAD_FOLDER, room_id)
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
        
        if room_id not in config.room_files:
            config.room_files[room_id] = []
            
        config.room_files[room_id].append(file_info)
        
        # Notify all users in the room about the new file
        current_app.handle_file_upload(file_info, room_id)
        
        return jsonify({
            "success": True, 
            "message": "File uploaded successfully!", 
            "file": file_info
        })
    
    return jsonify({"error": "File type not allowed"}), 400

@chat_bp.route('/<room_id>/files/<filename>', methods=['GET'])
def download_file(room_id, filename):
    client_ip = get_client_ip()
    password = request.args.get("password")
    
    if client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    # Find the file in room_files
    file_info = None
    if room_id in config.room_files:
        for file in config.room_files[room_id]:
            if file['stored_filename'] == filename:
                file_info = file
                break
    
    if not file_info:
        return jsonify({"error": "File not found"}), 404
    
    # Return the file
    return send_file(file_info['path'], as_attachment=True, download_name=file_info['filename'])

@chat_bp.route('/<room_id>/files', methods=['GET'])
def list_files(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")
    
    if client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if room_id not in config.room_files:
        return jsonify([])
    
    return jsonify(config.room_files[room_id])

@chat_bp.route('/<room_id>/files/<filename>', methods=['DELETE'])
def delete_file(room_id, filename):
    client_ip = get_client_ip()
    password = request.args.get("password")
    
    if client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    # Find the file in room_files
    file_info = None
    file_index = -1
    if room_id in config.room_files:
        for i, file in enumerate(config.room_files[room_id]):
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
            config.room_files[room_id].pop(file_index)
        
        # Notify all users in the room about file deletion
        current_app.handle_file_deletion(filename, room_id)
        
        return jsonify({"success": True, "message": "File deleted successfully!"})
    except Exception as e:
        return jsonify({"error": f"Error deleting file: {str(e)}"}), 500

@chat_bp.route('/<room_id>/search', methods=['GET'])
def search_messages(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")
    query = request.args.get("query", "").lower()
    
    if client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if not query:
        return jsonify({"error": "Search query is required"}), 400
    
    if room_id not in config.chat_rooms:
        return jsonify([])
    
    # Search through messages
    results = []
    for msg in config.chat_rooms[room_id]:
        if 'message' in msg and query in msg['message'].lower():
            results.append(msg)
    
    return jsonify({
        "success": True,
        "query": query,
        "results": results,
        "result_count": len(results)
    })

@chat_bp.route('/<room_id>/messages/<message_id>', methods=['DELETE'])
def delete_message(room_id, message_id):
    client_ip = get_client_ip()
    password = request.args.get("password")
    user_id = request.args.get("user_id")
    
    if client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    if room_id not in config.chat_rooms:
        return jsonify({"error": "Room not found"}), 404
    
    # Find the message
    message_index = -1
    message = None
    for i, msg in enumerate(config.chat_rooms[room_id]):
        if 'id' in msg and msg['id'] == message_id:
            message = msg
            message_index = i
            break
    
    if message_index == -1:
        return jsonify({"error": "Message not found"}), 404
    
    # Check if user is authorized to delete this message
    # Only the message sender or room admin (whoever has the password) can delete messages
    is_admin = config.room_passwords.get(room_id) == password
    is_sender = message.get('user_id') == user_id
    
    if not is_admin and not is_sender:
        return jsonify({"error": "Unauthorized to delete this message"}), 403
    
    # Remove the message
    removed_message = config.chat_rooms[room_id].pop(message_index)
    
    # Notify all users in the room about message deletion
    current_app.handle_message_deletion(message_id, user_id, is_admin and not is_sender, room_id)
    
    return jsonify({
        "success": True, 
        "message": "Message deleted successfully!",
        "deleted_message": removed_message
    })

@chat_bp.route('/<room_id>/messages/mark_read', methods=['POST'])
@token_required
def mark_messages_as_read(room_id):
    client_ip = get_client_ip()
    data = request.get_json()
    password = data.get("password")
    user_id = data.get("user_id")
    message_ids = data.get("message_ids", [])
    
    if not user_id:
        return jsonify({"success": False, "error": "User ID is required"}), 400
        
    if not message_ids or not isinstance(message_ids, list):
        return jsonify({"success": False, "error": "Message IDs must be provided as a list"}), 400
    
    # Check if authenticated via token
    if hasattr(request, 'is_authenticated') and request.is_authenticated and request.authenticated_room == room_id:
        pass  # Allow access if authenticated via token
    # Otherwise check IP or password
    elif client_ip not in config.room_verified_ips.get(room_id, []) and config.room_passwords.get(room_id) != password:
        return jsonify({"success": False, "error": "Access denied! Verify your IP or provide the correct password."}), 401
    
    # Initialize room if needed
    if room_id not in config.message_read_status:
        config.message_read_status[room_id] = {}
    
    # Mark messages as read
    updated_messages = []
    
    for message_id in message_ids:
        # If message exists in read status
        if message_id in config.message_read_status[room_id]:
            # Add user to read_by list if not already there
            if user_id not in config.message_read_status[room_id][message_id]['read_by']:
                config.message_read_status[room_id][message_id]['read_by'].append(user_id)
                updated_messages.append(message_id)
        
        # Also update the message in chat_rooms if it exists
        if room_id in config.chat_rooms:
            for i, encrypted_message in enumerate(config.chat_rooms[room_id]):
                message = decrypt_message(encrypted_message)
                if message.get('id') == message_id:
                    if 'read_by' not in message:
                        message['read_by'] = []
                    if user_id not in message['read_by']:
                        message['read_by'].append(user_id)
                        # Re-encrypt and update
                        config.chat_rooms[room_id][i] = encrypt_message(message)
                    break
    
    # Notify other users about read status change
    if hasattr(current_app, 'socketio'):
        current_app.socketio.emit('messages_read', {
            'room_id': room_id,
            'message_ids': updated_messages,
            'read_by': user_id
        }, room=room_id)
    
    return jsonify({
        "success": True,
        "updated_messages": updated_messages,
        "message": f"{len(updated_messages)} messages marked as read"
    }) 