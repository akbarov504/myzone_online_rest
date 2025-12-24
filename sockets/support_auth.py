from flask import request
from models.user import User
from flask_socketio import disconnect
from flask_jwt_extended import decode_token
import logging

# Logger
logger = logging.getLogger(__name__)

# Connected users
socket_users = {}

def authenticate_socket():
    """
    WebSocket connection uchun JWT token orqali autentifikatsiya
    """
    try:
        # 1. Token ni olish (query param yoki auth header'dan)
        token = None
        
        # Query parameter'dan
        if request.args.get("token"):
            token = request.args.get("token")
            logger.info(f"🔑 Token from query params")
        
        # Authorization header'dan (Socket.IO auth)
        elif hasattr(request, 'headers') and 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                logger.info(f"🔑 Token from Authorization header")
        
        # Socket.IO auth object'dan (client-side auth option)
        elif hasattr(request, 'environ'):
            # Socket.IO v4+ sends auth via handshake
            handshake_data = request.environ.get('socketio.handshake', {})
            auth_data = handshake_data.get('auth', {})
            if 'token' in auth_data:
                token = auth_data['token']
                logger.info(f"🔑 Token from Socket.IO auth")
        
        if not token:
            logger.warning("❌ No token provided")
            print("❌ AUTH FAILED: No token provided", flush=True)
            return None

        logger.info(f"🔍 Decoding token: {token[:20]}...")
        print(f"🔍 Attempting to decode token...", flush=True)
        
        # 2. Token ni decode qilish
        decoded = decode_token(token)
        logger.info(f"✅ Token decoded successfully")
        print(f"✅ Token decoded: {decoded}", flush=True)
        
        # 3. User ma'lumotlarini olish
        # JWT payload strukturasiga qarab
        user_id = decoded.get("sub")  # yoki decoded.get("user_id")
        
        if not user_id:
            logger.warning("❌ No user_id in token")
            print("❌ AUTH FAILED: No user_id in token", flush=True)
            return None
        
        logger.info(f"🔍 Looking up user: {user_id}")
        print(f"🔍 Looking up user: {user_id}", flush=True)
        
        # 4. Database'dan user ni topish
        # Agar sub username bo'lsa:
        user = User.query.filter_by(username=user_id).first()
        
        # Agar sub user ID bo'lsa:
        if not user:
            user = User.query.filter_by(id=user_id).first()
        
        if not user:
            logger.warning(f"❌ User not found: {user_id}")
            print(f"❌ AUTH FAILED: User not found - {user_id}", flush=True)
            return None
        
        logger.info(f"✅ User authenticated: {user.username} (ID: {user.id})")
        print(f"✅ AUTH SUCCESS: {user.username} (ID: {user.id}, Role: {user.role})", flush=True)
        
        return user
    
    except Exception as e:
        logger.error(f"❌ Authentication error: {str(e)}")
        print(f"❌ AUTH ERROR: {str(e)}", flush=True)
        import traceback
        print(traceback.format_exc(), flush=True)
        return None

def get_current_socket_user():
    """
    Joriy socket connection uchun user ni qaytaradi
    """
    return socket_users.get(request.sid)

def require_socket_auth(f):
    """
    Socket event uchun decorator - autentifikatsiyani tekshiradi
    """
    def decorated_function(*args, **kwargs):
        user = get_current_socket_user()
        if not user:
            logger.warning(f"❌ Unauthorized socket event: {f.__name__}")
            from flask_socketio import emit
            emit("error", {"message": "Authentication required"})
            disconnect()
            return None
        return f(user, *args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function