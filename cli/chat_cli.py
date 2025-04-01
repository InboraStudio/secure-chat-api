#!/usr/bin/env python3
import argparse
import requests
import json
import sys
import os
from typing import Optional
from datetime import datetime, timedelta

class ChatCLI:
    def __init__(self, base_url: str = "http://localhost:10000"):
        self.base_url = base_url.rstrip('/')
        self.token_file = os.path.join(os.path.dirname(__file__), ".auth_token")
        self.token = self._load_token()
        
    def _load_token(self) -> Optional[str]:
        """Load authentication token from file if it exists and is valid"""
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    expiry = datetime.fromisoformat(data['expiry'])
                    if expiry > datetime.now():
                        return data['token']
                    else:
                        print("⚠️ Auth token expired, will authenticate again")
            except Exception as e:
                print(f"⚠️ Error loading auth token: {e}")
        return None
        
    def _save_token(self, token: str, expiry_hours: int = 24):
        """Save authentication token to file with expiry time"""
        expiry = datetime.now() + timedelta(hours=expiry_hours)
        with open(self.token_file, 'w') as f:
            json.dump({
                'token': token,
                'expiry': expiry.isoformat()
            }, f)
            
    def _get_auth_headers(self, room_id: str, password: str) -> dict:
        """Get authentication headers, refreshing token if needed"""
        headers = {"Content-Type": "application/json"}
        
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            return headers
            
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/token",
                json={"room_id": room_id, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'token' in data:
                    self.token = data['token']
                    self._save_token(self.token)
                    headers["Authorization"] = f"Bearer {self.token}"
                    print("🔑 Authenticated successfully")
            else:
                print("⚠️ Could not authenticate, proceeding without token")
        except Exception as e:
            print(f"⚠️ Error authenticating: {e}")
            
        return headers
        
    def create_room(self, room_id: str, password: str) -> None:
        """Create a new chat room"""
        try:
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.base_url}/room/create",
                headers=headers,
                json={"room_id": room_id, "password": password}
            )
            response.raise_for_status()
            print(f"✅ Room {room_id} created successfully!")
            
            
            self._get_auth_headers(room_id, password)
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating room: {e}")
            sys.exit(1)

    def send_message(self, room_id: str, message: str, password: str, user_id: Optional[str] = None) -> None:
        """Send a message to a chat room"""
        try:
            headers = self._get_auth_headers(room_id, password)
            
            data = {
                "message": message,
                "password": password
            }
            if user_id:
                data["user_id"] = user_id
                
            response = requests.post(
                f"{self.base_url}/chat/{room_id}",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            print("✅ Message sent successfully!")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error sending message: {e}")
            sys.exit(1)

    def get_messages(self, room_id: str, password: Optional[str] = None, user_id: Optional[str] = None) -> None:
        """Get messages from a chat room"""
        try:
            headers = {}
            if password:
                headers = self._get_auth_headers(room_id, password)
                
            url = f"{self.base_url}/chat/{room_id}/messages"
            params = {}
            if password:
                params["password"] = password
            if user_id:
                params["user_id"] = user_id
               
                params["mark_as_read"] = "false"
            
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            if query_string:
                url += f"?{query_string}"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            messages = response.json()
            
            print("\n📬 Messages:")
            if not messages:
                print("   No messages found in this room.")
                return
            
          
            unread_count = 0
            unread_message_ids = []
                
            for msg in messages:
               
                timestamp = msg.get('time', 'Unknown time')
                user = msg.get('user_id', 'Anonymous')
                
                
                read_by = msg.get('read_by', [])
                read_count = len(read_by) if read_by else 0
                message_id = msg.get('id', 'unknown')
                
               
                if user_id and user_id == msg.get('user_id'):
                   
                    if read_count > 1:
                        status_icon = "🔵" 
                        read_status = f" [Read by {read_count - 1} users]"
                    else:
                        status_icon = "⚪" 
                        read_status = " [Unread]"
                else:
                   
                    if user_id and user_id in read_by:
                        status_icon = "🔵"  
                        read_status = " [Read]"
                    else:
                        status_icon = "⚪"  
                        read_status = " [Unread]"
                       
                        if user_id and user_id != msg.get('user_id'):
                            unread_count += 1
                            unread_message_ids.append(message_id)
                
                print(f"\n{status_icon} 👤 {user} ({timestamp}){read_status}:")
                print(f"   {msg.get('message', '')}")
                print(f"   ID: {msg.get('id', 'unknown')}")
                
          
            if unread_count > 0 and user_id:
                print(f"\n⚠️ You have {unread_count} unread messages")
                mark_read = input("Do you want to mark all as read? (y/n): ").lower().strip()
                if mark_read in ['y', 'yes']:
                    self.mark_read(room_id, unread_message_ids, password, user_id)
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting messages: {e}")
            sys.exit(1)

    def verify_ip(self, room_id: str, ip: str, password: str) -> None:
        """Verify a user's IP (Admin only)"""
        try:
            headers = self._get_auth_headers(room_id, password)
            
            response = requests.post(
                f"{self.base_url}/admin/verify_ip",
                headers=headers,
                json={"room_id": room_id, "ip": ip, "password": password}
            )
            response.raise_for_status()
            print(f"✅ IP {ip} verified for room {room_id}!")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error verifying IP: {e}")
            sys.exit(1)

    def clear_chat(self, room_id: str, password: str) -> None:
        """Clear all messages in a room"""
        try:
            headers = self._get_auth_headers(room_id, password)
            
            response = requests.post(
                f"{self.base_url}/chat/{room_id}/clear",
                headers=headers,
                json={"password": password}
            )
            response.raise_for_status()
            print(f"✅ Chat history cleared for room {room_id}!")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error clearing chat: {e}")
            sys.exit(1)

    def delete_room(self, room_id: str, password: str) -> None:
        """Delete a chat room (Admin only)"""
        try:
            headers = self._get_auth_headers(room_id, password)
            
            response = requests.post(
                f"{self.base_url}/admin/delete_room",
                headers=headers,
                json={"room_id": room_id, "password": password}
            )
            response.raise_for_status()
            print(f"✅ Room {room_id} deleted successfully!")
            
          
            if os.path.exists(self.token_file):
                os.remove(self.token_file)
                self.token = None
        except requests.exceptions.RequestException as e:
            print(f"❌ Error deleting room: {e}")
            sys.exit(1)
            
    def logout(self) -> None:
        """Remove saved authentication token"""
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
            self.token = None
            print("✅ Logged out successfully")
        else:
            print("ℹ️ No active session found")

    def mark_read(self, room_id: str, message_ids: list, password: str, user_id: str) -> None:
        """Mark messages as read"""
        try:
            headers = self._get_auth_headers(room_id, password)
            
            response = requests.post(
                f"{self.base_url}/chat/{room_id}/messages/mark_read",
                headers=headers,
                json={
                    "message_ids": message_ids,
                    "password": password,
                    "user_id": user_id
                }
            )
            response.raise_for_status()
            result = response.json()
            
            updated_count = len(result.get('updated_messages', []))
            if updated_count > 0:
                print(f"✅ {updated_count} messages marked as read")
            else:
                print("ℹ️ No new messages marked as read")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error marking messages as read: {e}")
            sys.exit(1)

    def mark_all_read(self, room_id: str, password: str, user_id: str) -> None:
        """Mark all messages in a room as read"""
        try:
          
            headers = self._get_auth_headers(room_id, password)
                
            url = f"{self.base_url}/chat/{room_id}/messages"
            params = {
                "password": password,
                "user_id": user_id,
                "mark_as_read": "false"  
            }
            
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            if query_string:
                url += f"?{query_string}"
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            messages = response.json()
            
          
            unread_message_ids = []
            for msg in messages:
                message_id = msg.get('id')
                read_by = msg.get('read_by', [])
                
               
                if message_id and user_id not in read_by and msg.get('user_id') != user_id:
                    unread_message_ids.append(message_id)
            
          
            if unread_message_ids:
                self.mark_read(room_id, unread_message_ids, password, user_id)
            else:
                print("📬 All messages are already marked as read")
        except requests.exceptions.RequestException as e:
            print(f"❌ Error marking all messages as read: {e}")
            sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Secure Chat CLI")
    parser.add_argument("--url", default="http://localhost:10000", help="Base URL of the chat server")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
  
    create_parser = subparsers.add_parser("create", help="Create a new chat room")
    create_parser.add_argument("room_id", help="5-digit room ID")
    create_parser.add_argument("password", help="Room password (min 8 chars)")
    
  
    send_parser = subparsers.add_parser("send", help="Send a message to a room")
    send_parser.add_argument("room_id", help="Room ID")
    send_parser.add_argument("message", help="Message to send")
    send_parser.add_argument("password", help="Room password")
    send_parser.add_argument("--user-id", help="User ID (defaults to 'cli-user')")
    
    
    get_parser = subparsers.add_parser("get", help="Get messages from a room")
    get_parser.add_argument("room_id", help="Room ID")
    get_parser.add_argument("--password", help="Room password (if IP not verified)")
    get_parser.add_argument("--user-id", help="User ID for message display")
    
   
    verify_parser = subparsers.add_parser("verify", help="Verify a user's IP (Admin only)")
    verify_parser.add_argument("room_id", help="Room ID")
    verify_parser.add_argument("ip", help="IP to verify")
    verify_parser.add_argument("password", help="Room password")
    
    
    clear_parser = subparsers.add_parser("clear", help="Clear chat history")
    clear_parser.add_argument("room_id", help="Room ID")
    clear_parser.add_argument("password", help="Room password")
    
   
    delete_parser = subparsers.add_parser("delete", help="Delete a room (Admin only)")
    delete_parser.add_argument("room_id", help="Room ID")
    delete_parser.add_argument("password", help="Room password")
    
    
    logout_parser = subparsers.add_parser("logout", help="Remove saved authentication tokens")
    

    mark_read_parser = subparsers.add_parser("mark_read", help="Mark messages as read")
    mark_read_parser.add_argument("room_id", help="Room ID")
    mark_read_parser.add_argument("message_ids", help="Comma-separated list of message IDs to mark as read")
    mark_read_parser.add_argument("password", help="Room password")
    mark_read_parser.add_argument("--user-id", required=True, help="User ID marking the messages as read")

    
    mark_all_parser = subparsers.add_parser("mark_all_read", help="Mark all messages in a room as read")
    mark_all_parser.add_argument("room_id", help="Room ID")
    mark_all_parser.add_argument("password", help="Room password")
    mark_all_parser.add_argument("--user-id", required=True, help="User ID marking the messages as read")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    cli = ChatCLI(args.url)
    
    if args.command == "create":
        cli.create_room(args.room_id, args.password)
    elif args.command == "send":
        cli.send_message(args.room_id, args.message, args.password, args.user_id)
    elif args.command == "get":
        cli.get_messages(args.room_id, args.password, args.user_id)
    elif args.command == "verify":
        cli.verify_ip(args.room_id, args.ip, args.password)
    elif args.command == "clear":
        cli.clear_chat(args.room_id, args.password)
    elif args.command == "delete":
        cli.delete_room(args.room_id, args.password)
    elif args.command == "logout":
        cli.logout()
    elif args.command == "mark_read":
        
        message_ids = [mid.strip() for mid in args.message_ids.split(',')]
        cli.mark_read(args.room_id, message_ids, args.password, args.user_id)
    elif args.command == "mark_all_read":
        cli.mark_all_read(args.room_id, args.password, args.user_id)

if __name__ == "__main__":
    main() 