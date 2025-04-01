from flask import Flask
from flask_socketio import SocketIO
from app.routes.chat import chat_bp
from app.socket_events.chat import register_socket_events
from app.config.config import HOST, PORT

def create_app():
    app = Flask(__name__)
    socketio = SocketIO(app)

    # Register blueprints
    app.register_blueprint(chat_bp)

    # Register socket events
    register_socket_events(socketio)

    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    
    # Get the local IP address
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"\nServer is running!")
    print(f"Local IP: {local_ip}")
    print(f"Access the chat at: http://{local_ip}:{PORT}")
    print("\nPress Ctrl+C to stop the server.\n")
    
    # Run the server
    socketio.run(app, host=HOST, port=PORT, debug=True) 