import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class SupportMessage(db.Model):
    __tablename__ = "support_message"

    id = db.Column(db.Integer(), primary_key=True)

    ticket_id = db.Column(db.Integer(), db.ForeignKey("support_ticket.id"), nullable=False)
    sender_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    sender_role = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, ticket_id, sender_id, sender_role, message):
        super().__init__()
        self.ticket_id = ticket_id
        self.sender_id = sender_id
        self.sender_role = sender_role
        self.message = message
    
    @staticmethod
    def to_dict(support_message):
        _ = {
            "id": support_message.id,
            "ticket_id": support_message.ticket_id,
            "sender_id": support_message.sender_id,
            "sender_role": support_message.sender_role,
            "message": support_message.message,
            "is_read": support_message.is_read,
            "created_at": str(support_message.created_at)
        }
        return _
