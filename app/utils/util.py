from flask import request, jsonify
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
import os
from app.models import User, db
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.environ.get('SECRET_KEY', 'secrets of secret places')

def encode_token(user_id):
    payload = {
        'exp': datetime.now(timezone.utc) + timedelta(days = 0, hours = 6),
        'iat': datetime.now(timezone.utc),
        'sub': str(user_id)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token



# def token_required(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs): 
#         token = None

#         if 'Authorization' in request.headers:
#             try: 
#                 token = request.headers['Authorization'].split()[1]

#                 payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
#                 print("PAYLOAD:", payload)

#                 request.user_id = payload['sub']
#             except jwt.ExpiredSignatureError:
#                 return jsonify({'message': "Token has expired"}), 401
#             except jwt.InvalidTokenError:
#                 return jsonify({"message": "Invalid Token"}), 401
#             return func(token_user=payload['sub'],*args, **kwargs) 
#         else:
#             return jsonify({"messages": "Token Authorization Required"}), 401
        
#     return wrapper

# def token_required(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs): 
#         token = None

#         # Check if token is in the Authorization header
#         if 'Authorization' in request.headers:
#             try: 
#                 # Extract the token
#                 token = request.headers['Authorization'].split()[1]  # Token is in the second part of the header
#                 print("Token received:", token)

#                 # Decode the token
#                 payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
#                 print("PAYLOAD:", payload)  # For debugging purposes

#                 # Attach the user ID to the request object
#                 request.user_id = payload['sub']
#             except jwt.ExpiredSignatureError:
#                 return jsonify({'message': "Token has expired"}), 401
#             except jwt.InvalidTokenError:
#                 return jsonify({"message": "Invalid Token"}), 401
            
#             return func(*args, **kwargs)  # Call the actual route function with user_id attached to request
#         else:
#             return jsonify({"message": "Token Authorization Required"}), 401
        
#     return wrapper

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None

        if request.method == "OPTIONS":
            return jsonify({"message": "CORS preflight passed"}), 200

        # Extract the token from the Authorization header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            print(f"Token received: {token}")  # Debugging

            # Decode the token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            print(f"Decoded payload: {payload}")  # Debugging

            # Fetch the current user using the user ID in the token's `sub` field
            current_user = db.session.get(User, payload['sub'])
            if not current_user:
                return jsonify({"message": "User not found!"}), 404
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired!"}), 401
        except jwt.InvalidTokenError as e:
            print(f"Invalid token error: {e}")  # Debugging
            return jsonify({"message": "Invalid token!"}), 401

        # Pass current_user to the route
        return func(current_user=current_user, *args, **kwargs)
    return decorated