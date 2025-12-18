import pytz
from models import db
from datetime import datetime
from flask_bcrypt import generate_password_hash

time_zone = pytz.timezone("Asia/Tashkent")

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer(), primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(13), nullable=False, unique=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    active_term = db.Column(db.Integer(), nullable=False)
    type_id = db.Column(db.Integer(), db.ForeignKey("type.id"), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, full_name, phone_number, username, password, role, active_term, type_id):
        super().__init__()
        self.full_name = full_name
        self.phone_number = phone_number
        self.username = username
        self.password = generate_password_hash(password).decode("utf-8")
        self.role = role
        self.active_term = active_term
        self.type_id = type_id

    @staticmethod
    def to_dict(user):
        _ = {
            "id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "username": user.username,
            "role": user.role,
            "active_term": user.active_term,
            "type_id": user.type_id,
            "is_active": user.is_active,
            "created_at": str(user.created_at)
        }
        return _
