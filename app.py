from flask import Flask, render_template, send_from_directory, make_response
from flask_socketio import SocketIO
import os
import socket
import config
from sockets.events import register_socket_events
from utils.helpers import get_local_ip

# Create Flask app
app = Flask(__name__, template_folder='UI', static_folder=None)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Add a route to serve static files from UI folder
@app.route('/styles.css')
def serve_css():
    response = make_response(send_from_directory('UI', 'styles.css'))
    response.headers['Content-Type'] = 'text/css'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/js/<path:filename>')
def serve_js(filename):
    response = make_response(send_from_directory('UI/js', filename))
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*", max_http_buffer_size=50 * 1024 * 1024)  # 50MB buffer

# Register socket events
socket_handlers = register_socket_events(socketio)

# Add socket handlers to app context
def handle_file_upload(file_info, room):
    socket_handlers['emit_file_uploaded'](file_info, room)

def handle_file_deletion(filename, room):
    socket_handlers['emit_file_deleted'](filename, room)

def handle_message_deletion(message_id, user_id, is_admin_delete, room):
    socket_handlers['emit_message_deleted'](message_id, user_id, is_admin_delete, room)

def handle_messages_read(room_id, message_ids, user_id):
    socket_handlers['emit_messages_read'](room_id, message_ids, user_id)

app.handle_file_upload = handle_file_upload
app.handle_file_deletion = handle_file_deletion
app.handle_message_deletion = handle_message_deletion
app.handle_messages_read = handle_messages_read
app.socketio = socketio  # Make socketio available to routes

# Register blueprints with url prefixes
from routes.chat_routes import chat_bp
from routes.user_routes import user_bp
from routes.room_routes import room_bp
from routes.admin_routes import admin_bp
from routes.auth_routes import auth_bp

app.register_blueprint(chat_bp, url_prefix='/chat')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(room_bp, url_prefix='/room')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(auth_bp, url_prefix='/auth')

# Define routes
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    local_ip = get_local_ip()
    
    print(f"\nServer is running!")
    print(f"Local IP: {local_ip}")
    print(f"Access the chat at: http://{local_ip}:{config.PORT}")
    print("\nPress Ctrl+C to stop the server.\n")
    
    socketio.run(app, host=config.HOST, port=config.PORT, debug=config.DEBUG) 