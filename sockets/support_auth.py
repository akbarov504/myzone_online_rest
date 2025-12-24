from flask import request
from models.user import User
from flask_socketio import disconnect
from flask_jwt_extended import decode_token

socket_users = {}

def authenticate_socket():
    token = request.args.get("token")
    if not token:
        return None

    try:
        decoded = decode_token(token)
        username = decoded["sub"]
        user = User.query.filter_by(username=username).first()
        return user
    
    except Exception:
        return None
