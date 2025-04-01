from flask_socketio import emit, join_room, leave_room
from flask import request
import time
from utils.helpers import format_date_time
import config

def register_socket_events(socketio):
    @socketio.on('join')
    def on_join(data):
        room = data['room']
        user_id = data['user_id']
        
        config.user_socket_map[user_id] = request.sid
        
        if room not in config.chat_rooms:
            config.chat_rooms[room] = []
        if room not in config.online_users:
            config.online_users[room] = set()
        if room not in config.message_reactions:
            config.message_reactions[room] = {}
        if room not in config.typing_users:
            config.typing_users[room] = set()
        if room not in config.room_files:
            config.room_files[room] = []
        
        join_room(room)
        config.online_users[room].add(user_id)
        
        emit('online_count', {
            'room': room,
            'count': len(config.online_users[room])
        }, room=room, broadcast=True)
        
        emit('status', {
            'msg': f'👋 {user_id} has joined the room'
        }, room=room, broadcast=True)
        
        # Send list of files in the room
        emit('files_list', {
            'room': room,
            'files': config.room_files[room]
        }, room=request.sid)

    @socketio.on('leave')
    def on_leave(data):
        room = data['room']
        user_id = data['user_id']
        
        if room in config.online_users:
            config.online_users[room].discard(user_id)
            if user_id in config.typing_users.get(room, set()):
                config.typing_users[room].discard(user_id)
            
            emit('online_count', {
                'room': room,
                'count': len(config.online_users[room])
            }, room=room, broadcast=True)
            
            emit('status', {
                'msg': f'👋 {user_id} has left the room'
            }, room=room, broadcast=True)

    @socketio.on('disconnect')
    def handle_disconnect():
        user_id = None
        for uid, sid in config.user_socket_map.items():
            if sid == request.sid:
                user_id = uid
                break
        
        if user_id:
            for room in list(config.online_users.keys()):
                if user_id in config.online_users[room]:
                    config.online_users[room].discard(user_id)
                    if user_id in config.typing_users.get(room, set()):
                        config.typing_users[room].discard(user_id)
                    
                    emit('online_count', {
                        'room': room,
                        'count': len(config.online_users[room])
                    }, room=room, broadcast=True)
                    
                    emit('status', {
                        'msg': f'👋 {user_id} has disconnected'
                    }, room=room, broadcast=True)
            
            del config.user_socket_map[user_id]

    @socketio.on('message')
    def handle_message(data):
        room = data['room']
        user_id = data['user_id']
        message = data['message']
        media = data.get('media', None)
        
        if room not in config.chat_rooms:
            config.chat_rooms[room] = []
        
        # Get user info
        username = config.user_profiles.get(user_id, {}).get('username', user_id)
        
        formatted_date, formatted_time = format_date_time()
        
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
        
        config.chat_rooms[room].append(message_data)
        
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
        
        if room not in config.typing_users:
            config.typing_users[room] = set()
        
        if is_typing:
            config.typing_users[room].add(user_id)
        else:
            config.typing_users[room].discard(user_id)
        
        emit('typing_status', {
            'room': room,
            'typing_users': list(config.typing_users[room])
        }, room=room)

    @socketio.on('reaction')
    def handle_reaction(data):
        room = data['room']
        message_id = data['message_id']
        user_id = data['user_id']
        reaction = data['reaction']
        
        if room not in config.message_reactions:
            config.message_reactions[room] = {}
        
        if message_id not in config.message_reactions[room]:
            config.message_reactions[room][message_id] = {}
            
        if reaction not in config.message_reactions[room][message_id]:
            config.message_reactions[room][message_id][reaction] = set()
            
        config.message_reactions[room][message_id][reaction].add(user_id)
        
        emit('reaction_update', {
            'message_id': message_id,
            'reactions': {
                r: list(users) for r, users in config.message_reactions[room][message_id].items()
            }
        }, room=room)
        
    # Function to emit file_uploaded event (called from chat_routes.py)
    def emit_file_uploaded(file_info, room):
        socketio.emit('file_uploaded', file_info, room=room)
    
    # Function to emit file_deleted event (called from chat_routes.py)
    def emit_file_deleted(filename, room):
        socketio.emit('file_deleted', {"filename": filename}, room=room)
    
    # Function to emit message_deleted event (called from chat_routes.py)
    def emit_message_deleted(message_id, user_id, is_admin_delete, room):
        socketio.emit('message_deleted', {
            "message_id": message_id,
            "deleted_by": user_id,
            "is_admin_delete": is_admin_delete
        }, room=room)

    # Function to emit messages_read event (called from chat_routes.py)
    def emit_messages_read(room_id, message_ids, user_id):
        socketio.emit('messages_read', {
            "room_id": room_id,
            "message_ids": message_ids,
            "read_by": user_id
        }, room=room_id)

    @socketio.on('mark_read')
    def handle_mark_read(data):
        room = data['room']
        user_id = data['user_id']
        message_ids = data['message_ids']
        
        if not room or not user_id or not message_ids or not isinstance(message_ids, list):
            return {"status": "error", "message": "Invalid input"}
        
        # Initialize room if needed
        if room not in config.message_read_status:
            config.message_read_status[room] = {}
        
        updated_messages = []
        
        for message_id in message_ids:
            # Update read status tracking
            if message_id not in config.message_read_status[room]:
                config.message_read_status[room][message_id] = {
                    'read_by': [user_id],
                    'timestamp': int(time.time() * 1000)
                }
                updated_messages.append(message_id)
            elif user_id not in config.message_read_status[room][message_id]['read_by']:
                config.message_read_status[room][message_id]['read_by'].append(user_id)
                updated_messages.append(message_id)
            
            # Update the actual message in chat_rooms if it exists
            if room in config.chat_rooms:
                for i, message in enumerate(config.chat_rooms[room]):
                    if isinstance(message, dict) and message.get('id') == message_id:
                        if 'read_by' not in message:
                            message['read_by'] = []
                        if user_id not in message['read_by']:
                            message['read_by'].append(user_id)
                        # No need to encrypt since we're updating the message object directly
                        break
        
        # Notify everyone that messages have been read
        if updated_messages:
            emit('messages_read', {
                'room_id': room,
                'message_ids': updated_messages,
                'read_by': user_id
            }, room=room, broadcast=True)
        
        return {"status": "success", "updated_messages": updated_messages}

    # Return the emit functions to be used in routes
    return {
        'emit_file_uploaded': emit_file_uploaded,
        'emit_file_deleted': emit_file_deleted,
        'emit_message_deleted': emit_message_deleted,
        'emit_messages_read': emit_messages_read
    } 