from flask import request, jsonify
from functools import wraps
from utils.helpers import verify_token

def token_required(f):
    """Decorator to require a valid JWT token for API access"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in the Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # If no token, proceed with normal authentication
        if not token:
            return f(*args, **kwargs)
            
        # Verify the token
        room_id = verify_token(token)
        
        # If token is invalid, proceed with normal authentication
        if not room_id:
            return f(*args, **kwargs)
            
        # If token is for a different room than requested, proceed with normal authentication
        if 'room_id' in kwargs and kwargs['room_id'] != room_id:
            return f(*args, **kwargs)
            
        # If token is valid for this room, set authenticated flag
        request.is_authenticated = True
        request.authenticated_room = room_id
            
        return f(*args, **kwargs)
    
    return decorated

def rate_limit(max_requests=60, time_window=60):
    """Decorator to apply rate limiting to API endpoints"""
    from time import time
    
    # Store request timestamps for each client
    request_history = {}
    
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr
            
            # Initialize request history for this client
            if client_ip not in request_history:
                request_history[client_ip] = []
                
            # Clean up old requests from history
            current_time = time()
            request_history[client_ip] = [
                timestamp for timestamp in request_history[client_ip]
                if current_time - timestamp < time_window
            ]
            
            # Check if client has exceeded rate limit
            if len(request_history[client_ip]) >= max_requests:
                return jsonify({
                    "success": False,
                    "error": "Rate limit exceeded. Please try again later."
                }), 429
                
            # Add current request to history
            request_history[client_ip].append(current_time)
            
            # Proceed with the original function
            return f(*args, **kwargs)
            
        return decorated
    
    return decorator 