import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer(), primary_key=True)

    user_payment_id = db.Column(db.Integer(), db.ForeignKey("user_payment.id"), nullable=False)
    amount = db.Column(db.Float(), nullable=False)
    type = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, user_payment_id, amount, type):
        super().__init__()
        self.user_payment_id = user_payment_id
        self.amount = amount
        self.type = type

    @staticmethod
    def to_dict(payment):
        _ = {
            "id": payment.id,
            "user_payment_id": payment.user_payment_id,
            "amount": payment.amount,
            "type": payment.type,
            "created_at": str(payment.created_at)
        }
        return _
