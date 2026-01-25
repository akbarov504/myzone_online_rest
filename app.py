# import logging
# from flask import Flask
# from flask_cors import CORS
# from flasgger import Swagger
# from flask_limiter import Limiter
# from flask_socketio import SocketIO
# from utils.utils import super_admin_create
# from models import db, bcrypt, jwt, migrate
# from flask_limiter.util import get_remote_address

# from routes.auth_route import auth_bp
# from routes.user_route import user_bp
# from routes.type_route import type_bp
# from routes.course_route import course_bp
# from routes.lesson_route import lesson_bp
# from routes.language_route import language_bp
# from routes.lesson_test_route import lesson_test_bp
# from routes.course_save_route import course_save_bp
# from routes.notification_route import notification_bp
# from routes.course_module_route import course_module_bp
# from routes.support_ticket_route import support_ticket_bp
# from routes.meeting_lesson_route import meeting_lesson_bp
# from routes.course_content_route import course_content_bp
# from routes.lesson_material_route import lesson_material_bp
# from routes.notification_user_route import notification_user_bp

# app = Flask(__name__)
# app.config['DEBUG'] = True
# app.config["SECRET_KEY"] = "dhq34155kjnjhjbu23uy545"
# app.config["JWT_SECRET_KEY"] = "dfgsk43jkh3kj4jhv23jdfw4jkh34kjh"
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://akbarov:akbarov@127.0.0.1:5432/my_zone_online_db"
# app.config["RATELIMIT_HEADERS_ENABLED"] = True
# app.config["RATELIMIT_STRATEGY"] = "moving-window"

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )

# app.logger.setLevel(logging.DEBUG)

# Swagger(app, template={
#     "info": {
#         "title": "My Zone Online API",
#         "description": "API documentation for My Zone Online platform",
#         "version": "1.0.0"
#     }
# })
# CORS(app)
# Limiter(app=app, key_func=get_remote_address, default_limits=["3000 per day", "500 per hour"])
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent", logger=True, engineio_logger=True)

# db.init_app(app)
# bcrypt.init_app(app)
# jwt.init_app(app)
# migrate.init_app(app, db)

# app.register_blueprint(auth_bp)
# app.register_blueprint(user_bp)
# app.register_blueprint(type_bp)
# app.register_blueprint(course_bp)
# app.register_blueprint(lesson_bp)
# app.register_blueprint(language_bp)
# app.register_blueprint(lesson_test_bp)
# app.register_blueprint(course_save_bp)
# app.register_blueprint(notification_bp)
# app.register_blueprint(course_module_bp)
# app.register_blueprint(support_ticket_bp)
# app.register_blueprint(meeting_lesson_bp)
# app.register_blueprint(course_content_bp)
# app.register_blueprint(lesson_material_bp)
# app.register_blueprint(notification_user_bp)

# with app.app_context():
#     db.create_all()
#     super_admin_create()

# if __name__ == "__main__":
#     socketio.run(app, port=8080, debug=True, use_reloader=True, log_output=True, host="0.0.0.0")



# v2 ==============================================
# import logging
# from flask import Flask
# from flask_cors import CORS
# from flasgger import Swagger
# from flask_limiter import Limiter
# from flask_socketio import SocketIO
# from utils.utils import super_admin_create
# from models import db, bcrypt, jwt, migrate
# from flask_limiter.util import get_remote_address

# from routes.auth_route import auth_bp
# from routes.user_route import user_bp
# from routes.type_route import type_bp
# from routes.course_route import course_bp
# from routes.lesson_route import lesson_bp
# from routes.language_route import language_bp
# from routes.lesson_test_route import lesson_test_bp
# from routes.course_save_route import course_save_bp
# from routes.notification_route import notification_bp
# from routes.course_module_route import course_module_bp
# from routes.support_ticket_route import support_ticket_bp
# from routes.meeting_lesson_route import meeting_lesson_bp
# from routes.course_content_route import course_content_bp
# from routes.lesson_material_route import lesson_material_bp
# from routes.notification_user_route import notification_user_bp

# app = Flask(__name__)
# app.config['DEBUG'] = True
# app.config["SECRET_KEY"] = "dhq34155kjnjhjbu23uy545"
# app.config["JWT_SECRET_KEY"] = "dfgsk43jkh3kj4jhv23jdfw4jkh34kjh"
# app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://akbarov:akbarov@127.0.0.1:5432/my_zone_online_db"
# app.config["RATELIMIT_HEADERS_ENABLED"] = True
# app.config["RATELIMIT_STRATEGY"] = "moving-window"

# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )

# app.logger.setLevel(logging.DEBUG)

# Swagger(app, template={
#     "info": {
#         "title": "My Zone Online API",
#         "description": "API documentation for My Zone Online platform",
#         "version": "1.0.0"
#     }
# })
# CORS(app)
# Limiter(app=app, key_func=get_remote_address, default_limits=["3000 per day", "500 per hour"])
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent", logger=True, engineio_logger=True)

# db.init_app(app)
# bcrypt.init_app(app)
# jwt.init_app(app)
# migrate.init_app(app, db)

# app.register_blueprint(auth_bp)
# app.register_blueprint(user_bp)
# app.register_blueprint(type_bp)
# app.register_blueprint(course_bp)
# app.register_blueprint(lesson_bp)
# app.register_blueprint(language_bp)
# app.register_blueprint(lesson_test_bp)
# app.register_blueprint(course_save_bp)
# app.register_blueprint(notification_bp)
# app.register_blueprint(course_module_bp)
# app.register_blueprint(support_ticket_bp)
# app.register_blueprint(meeting_lesson_bp)
# app.register_blueprint(course_content_bp)
# app.register_blueprint(lesson_material_bp)
# app.register_blueprint(notification_user_bp)

# with app.app_context():
#     db.create_all()
#     super_admin_create()

# if __name__ == "__main__":
#     socketio.run(app, port=8080, debug=True, use_reloader=False, log_output=True, host="0.0.0.0")



# ============================================================
# GEVENT MONKEY PATCH — ENG MUHIM (1-QATORDA BO‘LISHI SHART)
# ============================================================
from gevent import monkey
monkey.patch_all()

# ============================================================
# STANDARD IMPORTS
# ============================================================
import logging
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

# ============================================================
# APP EXTENSIONS
# ============================================================
from models import db, bcrypt, jwt, migrate
from utils.utils import super_admin_create

# ============================================================
# ROUTES (BLUEPRINTS)
# ============================================================
from routes.auth_route import auth_bp
from routes.user_route import user_bp
from routes.type_route import type_bp
from routes.course_route import course_bp
from routes.lesson_route import lesson_bp
from routes.language_route import language_bp
from routes.lesson_test_route import lesson_test_bp
from routes.course_save_route import course_save_bp
from routes.notification_route import notification_bp
from routes.course_module_route import course_module_bp
from routes.support_ticket_route import support_ticket_bp
from routes.meeting_lesson_route import meeting_lesson_bp
from routes.course_content_route import course_content_bp
from routes.lesson_material_route import lesson_material_bp
from routes.notification_user_route import notification_user_bp

# ============================================================
# CREATE FLASK APP
# ============================================================
app = Flask(__name__)

# ============================================================
# CONFIGURATION
# ============================================================
app.config.update(
    DEBUG=True,

    # Security
    SECRET_KEY="dhq34155kjnjhjbu23uy545",
    JWT_SECRET_KEY="dfgsk43jkh3kj4jhv23jdfw4jkh34kjh",
    JWT_ACCESS_TOKEN_EXPIRES=3600,

    # Database
    SQLALCHEMY_DATABASE_URI="postgresql://akbarov:akbarov@127.0.0.1:5432/my_zone_online_db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,

    # DEBUG: SQL ko‘rish uchun (prod’da o‘chiriladi)
    SQLALCHEMY_ECHO=True,

    # Rate limit
    RATELIMIT_HEADERS_ENABLED=True,
    RATELIMIT_STRATEGY="moving-window",
)

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
app.logger.setLevel(logging.INFO)

# ============================================================
# SWAGGER
# ============================================================
Swagger(app, template={
    "info": {
        "title": "My Zone Online API",
        "description": "API documentation for My Zone Online platform",
        "version": "1.0.0"
    }
})

# ============================================================
# CORS (SOCKET + API)
# ============================================================
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
    supports_credentials=True
)

# ============================================================
# RATE LIMITER
# ============================================================
Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["500 per hour"]
)

# ============================================================
# SOCKET.IO INITIALIZATION (YAGONA INSTANCE)
# ============================================================
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="gevent",
    logger=False,
    engineio_logger=False,
    ping_interval=25,
    ping_timeout=60,
)

# ============================================================
# INIT EXTENSIONS
# ============================================================
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
migrate.init_app(app, db)

# ============================================================
# REGISTER BLUEPRINTS
# ============================================================
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(type_bp)
app.register_blueprint(course_bp)
app.register_blueprint(lesson_bp)
app.register_blueprint(language_bp)
app.register_blueprint(lesson_test_bp)
app.register_blueprint(course_save_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(course_module_bp)
app.register_blueprint(support_ticket_bp)
app.register_blueprint(meeting_lesson_bp)
app.register_blueprint(course_content_bp)
app.register_blueprint(lesson_material_bp)
app.register_blueprint(notification_user_bp)

# ============================================================
# SOCKET HANDLERS (ALOHIDA FAYLDAN)
# ============================================================
from sockets.support_chat import register_socket_handlers
register_socket_handlers(socketio)

# ============================================================
# DB INIT + SUPER ADMIN
# ============================================================
with app.app_context():
    db.create_all()
    super_admin_create()

# ============================================================
# HEALTH CHECK
# ============================================================
@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "my-zone-online-backend"
    }, 200

# ============================================================
# MAIN ENTRY POINT
# ============================================================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 MY ZONE ONLINE BACKEND IS STARTING")
    print("=" * 60)
    print("🌐 API      → http://0.0.0.0:8080")
    print("📡 SOCKET   → ws://0.0.0.0:8080")
    print("=" * 60 + "\n")

    socketio.run(
        app,
        host="0.0.0.0",
        port=8080,
        debug=True,
        use_reloader=False,   # ❗️❗️ SHART (AKS HOLDA DB YOZILMAYDI)
    )