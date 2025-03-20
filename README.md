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
git clone https://github.com/yourusername/chatting-api.git
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

---

## 🎯 **API Endpoints**
### **1️⃣ Send a Message (With Authentication Token or Verified IP)**
```bash
curl -X POST https://chattingcurl.onrender.com/chat/12345 \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -d '{"message": "Hello from Flash!"}'
```
🔹 **Replaces `12345` with the room ID**.  
🔹 **Message will be stored and displayed in the chat room**.  
🔹 **Requires authentication token OR verified IP approval from the room creator**.

---

### **2️⃣ Get All Messages in a Room (Requires Token or Verified IP)**
```bash
curl -X GET https://chattingcurl.onrender.com/chat/12345 \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
🔹 **Returns all messages stored in `12345` in JSON format**.  
🔹 **Requires authentication token OR IP verification**.

---

### **3️⃣ View Messages in a Browser (Password-Protected)**
Simply open:
```
https://chattingcurl.onrender.com/chat/12345/web?token=YOUR_ACCESS_TOKEN&password=ROOM_PASSWORD
```
🔹 **Now, only authenticated users or those with the correct password can access chat rooms**.  
🔹 **If IP is verified by the room creator, no password is needed**.

---

### **4️⃣ Clear Chat Messages (Secure & Verified)**
```bash
curl -X POST https://chattingcurl.onrender.com/chat/12345/clear \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```
🔹 **Deletes all messages in `12345`**.  
🔹 **Only room creator or authorized users can clear messages**.

---

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
