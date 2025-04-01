# Secure Chat CLI Tool

A command-line interface for the Secure Chat API that allows you to manage chat rooms and messages directly from the terminal.

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:
```bash
python -m pip install requests
```
Note: Make sure to install requests in the same Python environment you'll be using to run the CLI.

## Important Notes

- The server must be running before using the CLI tool
- Room IDs must be exactly 5 digits (e.g., "12345")
- Passwords must be at least 8 characters long
- When sending messages, use the `--user-id` parameter to identify yourself
- For retrieving messages, include the `--password` parameter if your IP isn't verified

## Usage

The CLI tool provides several commands to interact with the chat server. Here are some examples:

### Create a New Chat Room
```bash
python cli/chat_cli.py create 12345 password123
```

### Send a Message
```bash
python cli/chat_cli.py send 12345 "Hello, world!" password123 --user-id your-username
```

### Get Messages
```bash
# If your IP is verified:
python cli/chat_cli.py get 12345

# If your IP is not verified:
python cli/chat_cli.py get 12345 --password password123
```

### Verify a User's IP (Admin Only)
```bash
python cli/chat_cli.py verify 12345 192.168.1.100 password123
```

### Clear Chat History
```bash
python cli/chat_cli.py clear 12345 password123
```

### Delete a Room (Admin Only)
```bash
python cli/chat_cli.py delete 12345 password123
```

### Using a Different Server URL
```bash
python cli/chat_cli.py --url http://your-server:10000 create 12345 password123
```

## Troubleshooting

If you encounter errors when using the CLI:

1. **ModuleNotFoundError: No module named 'requests'**
   - Install the requests library: `python -m pip install requests`
   - Make sure to use the same Python interpreter for both installing and running

2. **401 Unauthorized Errors**
   - Verify that you're using the correct room ID and password
   - Include the `--user-id` parameter when sending messages
   - For certain operations, your IP might need to be verified first

3. **400 Bad Request Errors**
   - Check that your room ID is exactly 5 digits
   - Ensure your password is at least 8 characters long

4. **Connection Errors**
   - Make sure the server is running
   - Check that you're using the correct server URL

## Security Features

The CLI tool maintains the same security standards as the web interface:

- 🔐 Password authentication required for all operations
- 🔒 Messages are encrypted before being sent to the server
- 🌐 IP verification support for trusted access
- 🔑 User ID required for message attribution
- 👑 Admin operations for room management
- 🛡️ Secure communication with the server using HTTPS (when server supports it)

## Command Reference

### Global Options
- `--url`: Base URL of the chat server (default: http://localhost:10000)

### Commands

#### `create`
Create a new chat room
```bash
python cli/chat_cli.py create <room_id> <password>
```

#### `send`
Send a message to a room
```bash
python cli/chat_cli.py send <room_id> "<message>" <password> [--user-id <user_id>]
```

#### `get`
Get messages from a room
```bash
python cli/chat_cli.py get <room_id> [--password <password>] [--user-id <user_id>]
```

#### `verify`
Verify a user's IP (Admin only)
```bash
python cli/chat_cli.py verify <room_id> <ip> <password>
```

#### `clear`
Clear chat history
```bash
python cli/chat_cli.py clear <room_id> <password>
```

#### `delete`
Delete a room (Admin only)
```bash
python cli/chat_cli.py delete <room_id> <password>
```

## Requirements
- Python 3.6 or higher
- `requests` library

## Notes
- Room IDs must be 5 digits
- Passwords must be at least 8 characters long
- Some commands require admin privileges
- The server must be running before using the CLI tool 