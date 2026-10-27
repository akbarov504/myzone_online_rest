import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class UserPayment(db.Model):
    __tablename__ = "user_payment"

    id = db.Column(db.Integer(), primary_key=True)

    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(13), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    active_term = db.Column(db.Integer(), nullable=False)
    type_id = db.Column(db.Integer(), db.ForeignKey("type.id"), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)
    profile_image = db.Column(db.Text(), nullable=True)

    discount = db.Column(db.Float(), nullable=False, default=0)
    course_price = db.Column(db.Float(), nullable=False, default=2_000_000)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, user_id, full_name, phone_number, username, role, active_term, type_id, is_active, profile_image, discount=0, course_price=2_000_000):
        super().__init__()
        self.user_id = user_id
        self.full_name = full_name
        self.phone_number = phone_number
        self.username = username
        self.role = role
        self.active_term = active_term
        self.type_id = type_id
        self.is_active = is_active
        self.profile_image = profile_image
        self.discount = discount
        self.course_price = course_price

    @staticmethod
    def to_dict(user_payment):
        _ = {
            "id": user_payment.id,
            "user_id": user_payment.user_id,
            "full_name": user_payment.full_name,
            "phone_number": user_payment.phone_number,
            "username": user_payment.username,
            "role": user_payment.role,
            "active_term": user_payment.active_term,
            "type_id": user_payment.type_id,
            "is_active": user_payment.is_active,
            "profile_image": user_payment.profile_image,
            "discount": user_payment.discount,
            "course_price": user_payment.course_price,
            "created_at": str(user_payment.created_at)
        }
        return _
