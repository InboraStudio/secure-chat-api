from flask_socketio import emit, join_room, leave_room
from app.utils.helpers import get_current_time
from app.config.config import MAX_MESSAGES_PER_ROOM

chat_rooms = {}
room_passwords = {}
room_verified_ips = {}
user_profiles = {}
online_users = {}
message_reactions = {}
typing_users = {}
user_socket_map = {}

def register_socket_events(socketio):
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

    @socketio.on('message')
    def handle_message(data):
        room = data['room']
        user_id = data['user_id']
        message = data['message']
        
        if room not in chat_rooms:
            chat_rooms[room] = []
        
        time_data = get_current_time()
        message_data = {
            'user_id': user_id,
            'message': message,
            'timestamp': time_data['timestamp'],
            'date': time_data['date'],
            'time': time_data['time'],
            'is_sent': True
        }
        
        chat_rooms[room].append(message_data)
        
        if len(chat_rooms[room]) > MAX_MESSAGES_PER_ROOM:
            chat_rooms[room] = chat_rooms[room][-MAX_MESSAGES_PER_ROOM:]
        
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
            'room': room,
            'user_id': user_id,
            'is_typing': is_typing
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