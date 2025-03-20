# 📨 Chatting API with Room Access (Flask + cURL)

A simple **chat application** built with **Flask**, where users can send and receive messages in **chat rooms** using `curl` or a **web interface**.

---

## 🌟 Features
- 🔹 **Room-based messaging** (Each chat room has a unique 5-digit ID)
- 🔹 **Store messages in memory**
- 🔹 **View messages in a web browser**
- 🔹 **Clear chat messages with a single click**
- 🔹 **Supports `curl` for sending & retrieving messages**
- 🔹 **Includes sender's IP address in messages**
- 🔹 **Deployed on Render.com**
- 🔒 **Secure chat rooms with access tokens**
- 🔒 **End-to-end encryption for messages**
- 🔒 **User authentication for private rooms**
- 🔒 **IP-based verification by room creator**
- 🔒 **Password-protected room access**

---

## 🚀 **Live Demo**
🔗 [Chat API Hosted on Render](https://chattingcurl.onrender.com)

---

## 📂 **Project Structure**
```
/chat_project
│── /templates
│   └── chat.html       # Web UI for viewing messages
│── server.py           # Flask API handling chat messages
│── requirements.txt    # Required dependencies for deployment
│── README.md           # Project documentation
```

---

## 🔧 **Installation & Setup (Run Locally)**
1️⃣ **Clone the repository**  
```bash
git clone https://github.com/DHIRAJ-GHOLAP/secure-chat-api.git
cd chatting-api
```

2️⃣ **Install dependencies**  
```bash
pip install -r requirements.txt
```

3️⃣ **Run the server**  
```bash
python server.py
```

4️⃣ **Access the chat application**  
- Open your browser and go to:
  ```
  http://127.0.0.1:10000/chat/12345/web
  ```
- Replace `12345` with any **5-digit room number**.

# 🚀 Secure Chat API - cURL Commands

This document contains all **cURL commands** needed to manage **chat rooms, messages, admin functionalities, and authentication** in the **Secure Chat API**.

---

## **📌 Chat Room Management**

### **1️⃣ Create a New Chat Room**
```bash
curl -X POST "https://chattingcurl.onrender.com/room/create" -H "Content-Type: application/json" -d '{"room_id":"12345","password":"securepass"}'
```
📌 **Replace** `12345` with your room ID and `securepass` with your room password.

---

## **📩 Messaging System**

### **2️⃣ Send a Message to a Chat Room**
```bash
curl -X POST "https://chattingcurl.onrender.com/chat/12345" -H "Content-Type: application/json" -d '{"message":"Hello world!","password":"securepass"}'
```
📌 **Replace** `12345` with your room ID and `securepass` with your room password.

### **3️⃣ Get Messages from a Chat Room (If IP is Verified, No Password Needed)**
```bash
curl -X GET "https://chattingcurl.onrender.com/chat/12345"
```
📌 **Only works for verified IP users!**

### **4️⃣ Get Messages Using Password (If IP is NOT Verified)**
```bash
curl -X GET "https://chattingcurl.onrender.com/chat/12345?password=securepass"
```
📌 **Use the password if your IP is not verified.**

### **5️⃣ View Chat Messages in Web Browser**
```bash
curl -X GET "https://chattingcurl.onrender.com/chat/12345/web?password=securepass"
```
📌 **Opens chat messages in a web-based UI.**

---

## **🔐 Admin Panel Commands**

### **6️⃣ Verify a User's IP (Admin Only)**
```bash
curl -X POST "https://chattingcurl.onrender.com/admin/verify_ip" -H "Content-Type: application/json" -d '{"room_id":"12345","ip":"192.168.1.10","password":"securepass"}'
```
📌 **Replace `192.168.1.10` with the IP you want to verify.**

### **7️⃣ Clear All Messages in a Room (Admin Only)**
```bash
curl -X POST "https://chattingcurl.onrender.com/admin/clear_chat" -H "Content-Type: application/json" -d '{"room_id":"12345","password":"securepass"}'
```
📌 **Only admins can clear chat history.**

### **8️⃣ Delete a Chat Room (Admin Only)**
```bash
curl -X POST "https://chattingcurl.onrender.com/admin/delete_room" -H "Content-Type: application/json" -d '{"room_id":"12345","password":"securepass"}'
```
📌 **Removes the chat room and all its data.**

---

## **🌍 Miscellaneous Commands**

### **9️⃣ Check Your Public IP (For Verification)**
```bash
curl ifconfig.me
```
📌 **Use this command to find your IP before requesting admin verification.**

### **🔟 Clear Messages in a Room (For Any User with Access)**
```bash
curl -X POST "https://chattingcurl.onrender.com/chat/12345/clear" -H "Content-Type: application/json" -d '{"password":"securepass"}'
```
📌 **Allows authorized users to clear chat messages.**

---

# ✅ **Now Your Chat API is Ready to Use!** 🚀
💡 **Let me know if you need additional features or security improvements!** 😊

# ✅ **Now Your Chat API is Ready to Use!** 🚀
💡 **Let me know if you need additional features or security improvements!** 😊


## 🔐 **Security Features Added**
- ✅ **Access tokens required for all API requests**
- ✅ **Messages encrypted before storing**
- ✅ **Users must authenticate to access private chat rooms**
- ✅ **Web interface requires authentication**
- ✅ **Room creator can verify user IP for automatic access**
- ✅ **Password-protected chat rooms for privacy**

---

## 🌐 **Deploying on Render**
1️⃣ **Push your code to GitHub**  
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2️⃣ **Deploy on Render**
- Go to [Render.com](https://dashboard.render.com/)
- Click **"New Web Service"**
- Select **GitHub Repository**
- Set **Runtime**: `Python 3.x`
- Set **Start Command**:  
  ```bash
  python server.py
  ```
- **Deploy! 🎉**

---

## 🛠 **Future Improvements**
- ✅ **Database storage for messages (PostgreSQL)**
- ✅ **WebSockets for real-time chat**
- ✅ **User authentication with JWT**
- ✅ **End-to-end encryption for messages**
- ✅ **Two-factor authentication for room access**

---

## 🎖 **Contributors**
👤 **Dhiraj (Flash)**  
🔗 GitHub: [DHIRAJ-GHOLAP](https://github.com/DHIRAJ-GHOLAP)

Feel free to contribute, fork, or improve this project! 🚀
