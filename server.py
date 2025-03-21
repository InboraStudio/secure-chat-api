from flask import Flask, request, jsonify, render_template
import jwt
import datetime
import os

app = Flask(__name__)

# Secret keys for JWT authentication
SECRET_KEY = os.getenv("SECRET_KEY", "mysecretkey")
JWT_SECRET = os.getenv("JWT_SECRET", "supersecret")

# Store messages securely
chat_rooms = {}
room_passwords = {}
room_verified_ips = {}

# Function to generate a JWT token for authentication
def generate_token(room_id):
    payload = {
        "room_id": room_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")



# **FIXED: Clear Chat Route**
@app.route('/chat/<room_id>/clear', methods=['POST'])
def clear_chat(room_id):
    if room_id in chat_rooms:
        chat_rooms[room_id] = []
    return jsonify({"success": True, "message": "Chat cleared!"})

# Function to verify JWT token
def verify_token(token):
    try:
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded["room_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# Function to get client's IP
def get_client_ip():
    return request.headers.get("X-Forwarded-For", request.remote_addr)

# Default homepage route
@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Secure Chat API 🚀</title>
        <style>
            /* Global Styles */
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f0f2f5;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }

            .container {
                max-width: 600px;
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                text-align: center;
            }

            h2 {
                color: #333;
                margin-bottom: 10px;
            }

            p {
                color: #666;
                font-size: 14px;
                margin-bottom: 20px;
            }

            ul {
                text-align: left;
                list-style: none;
                padding: 0;
            }

            li {
                background: #e3f2fd;
                padding: 10px;
                margin: 5px 0;
                border-radius: 5px;
                font-size: 14px;
            }

            a {
                text-decoration: none;
                color: #007bff;
                font-weight: bold;
            }

            hr {
                border: 0;
                height: 1px;
                background: #ddd;
                margin: 20px 0;
            }

            /* Form Styles */
            .form-group {
                text-align: left;
                margin-bottom: 15px;
            }

            label {
                font-weight: bold;
                font-size: 14px;
                display: block;
                margin-bottom: 5px;
            }

            input {
                width: 100%;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }

            .btn {
                width: 100%;
                padding: 12px;
                background: #007bff;
                color: white;
                border: none;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                border-radius: 5px;
                transition: all 0.3s ease;
            }

            .btn:hover {
                background: #0056b3;
            }

            /* Responsive Design */
            @media (max-width: 600px) {
                .container {
                    width: 90%;
                    padding: 20px;
                }
            }
        </style>
    </head>
    <body>

        <div class="container">
            <h2>Welcome to Secure Chat API 🚀</h2>
            <p>A secure chat system with **IP verification and password protection**.</p>
            
            <h3>📌 API Endpoints:</h3>
            <ul>
                <li>🔹 <strong>Create Room:</strong> <code>POST /room/create</code></li>
                <li>🔹 <strong>Verify IP:</strong> <code>POST /room/&lt;room_id&gt;/verify_ip</code></li>
                <li>🔹 <strong>View Chat Room:</strong> <a href="/chat/12345/web?password=securepass"><code>/chat/&lt;room_id&gt;/web</code></a></li>
                <li>🔹 <strong>Send Message:</strong> <code>POST /chat/&lt;room_id&gt;</code></li>
                <li>🔹 <strong>Get Messages:</strong> <code>GET /chat/&lt;room_id&gt;</code></li>
            </ul>

            <hr>

            <h3>📝 Create a New Chat Room</h3>
            <form method="POST" action="/room/create">
                <div class="form-group">
                    <label>Room ID:</label>
                    <input type="text" name="room_id" required>
                </div>

                <div class="form-group">
                    <label>Password:</label>
                    <input type="password" name="password" required>
                </div>

                <button type="submit" class="btn">Create Room</button>
            </form>
        </div>

    </body>
    </html>
    """

from flask import request

@app.route('/room/create', methods=['POST'])
def create_room():
    # Check if request is JSON or form data
    if request.content_type == "application/json":
        data = request.get_json()
        room_id = data.get("room_id")
        password = data.get("password")
    else:
        room_id = request.form.get("room_id")
        password = request.form.get("password")

    # Validate inputs
    if not room_id or not password:
        return jsonify({"error": "Room ID and password are required!"}), 400

    room_passwords[room_id] = password
    room_verified_ips[room_id] = []
    chat_rooms[room_id] = []

    return jsonify({"success": True, "message": f"Room {room_id} created successfully!"})

# Route to verify an IP (Room creator must approve)
@app.route('/room/<room_id>/verify_ip', methods=['POST'])
def verify_ip(room_id):
    data = request.get_json()
    password = data.get("password")
    user_ip = data.get("ip")  # Room creator submits the IP to be allowed

    if room_passwords.get(room_id) != password:
        return jsonify({"error": "Invalid password!"}), 401

    if room_id not in room_verified_ips:
        room_verified_ips[room_id] = []

    room_verified_ips[room_id].append(user_ip)

    return jsonify({"success": True, "message": f"IP {user_ip} verified for room {room_id}!"})

# Route to send a message (Only if IP verified or password provided)
@app.route('/chat/<room_id>', methods=['POST'])
def send_message(room_id):
    client_ip = get_client_ip()
    data = request.get_json()
    message = data.get("message")
    password = data.get("password")

    # Verify access: Either IP must be verified or correct password must be provided
    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return jsonify({"error": "Access denied! Verify your IP or provide the correct password."}), 401

    if room_id not in chat_rooms:
        chat_rooms[room_id] = []

    chat_rooms[room_id].append(f"[{client_ip}] {message}")
    return jsonify({"success": True, "message": "Message sent securely!"})
@app.route('/chat/<room_id>', methods=['GET'])
def get_messages(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")

    # 🔍 Debugging: Print client IP and verified IPs list
    print(f"Client IP: {client_ip}")
    print(f"Verified IPs for Room {room_id}: {room_verified_ips.get(room_id, [])}")

    # ✅ Allow access if the user's IP is verified OR they provide the correct password
    if client_ip in room_verified_ips.get(room_id, []) or room_passwords.get(room_id) == password:
        messages = chat_rooms.get(room_id, [])
        return jsonify({"messages": messages})
    
    return jsonify({"error": "Access denied! Your IP is not verified and no valid password provided."}), 401

# Route to view messages in a browser (Password-Protected)
@app.route('/chat/<room_id>/web', methods=['GET'])
def chat_web(room_id):
    client_ip = get_client_ip()
    password = request.args.get("password")

    if client_ip not in room_verified_ips.get(room_id, []) and room_passwords.get(room_id) != password:
        return "<h3>Access Denied! Verify your IP or provide the correct password.</h3>", 401

    messages = chat_rooms.get(room_id, [])
    return render_template("chat.html", room_id=room_id, messages=messages)


# ✅ Admin Dashboard Route
@app.route('/admin')
def admin_panel():
    return render_template("admin.html")

# ✅ Admin Route: Verify a User's IP
@app.route('/admin/verify_ip', methods=['POST'])
def admin_verify_ip():
    room_id = request.form.get("room_id")
    ip = request.form.get("ip")
    password = request.form.get("password")

    if not room_id or not ip or not password:
        return jsonify({"error": "All fields are required!"}), 400

    # Check if the password is correct
    if room_passwords.get(room_id) != password:
        return jsonify({"error": "Unauthorized access!"}), 401

    # Add the IP to the verified list
    if room_id not in room_verified_ips:
        room_verified_ips[room_id] = []
    
    room_verified_ips[room_id].append(ip)
    return jsonify({"success": True, "message": f"IP {ip} verified for room {room_id}!"})

# ✅ Admin Route: Clear Chat Messages
@app.route('/admin/clear_chat', methods=['POST'])
def admin_clear_chat():
    room_id = request.form.get("room_id")
    password = request.form.get("password")

    if room_passwords.get(room_id) != password:
        return jsonify({"error": "Unauthorized access!"}), 401

    if room_id in chat_rooms:
        chat_rooms[room_id] = []
    return jsonify({"success": True, "message": "Chat cleared successfully!"})

# ✅ Admin Route: Delete Chat Room
@app.route('/admin/delete_room', methods=['POST'])
def admin_delete_room():
    room_id = request.form.get("room_id")
    password = request.form.get("password")

    if room_passwords.get(room_id) != password:
        return jsonify({"error": "Unauthorized access!"}), 401

    chat_rooms.pop(room_id, None)
    room_verified_ips.pop(room_id, None)
    room_passwords.pop(room_id, None)
    return jsonify({"success": True, "message": f"Room {room_id} deleted!"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
