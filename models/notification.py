import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text(), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    is_global = db.Column(db.Boolean(), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, title, message, type, is_global):
        super().__init__()
        self.title = title
        self.message = message
        self.type = type
        self.is_global = is_global
    
    @staticmethod
    def to_dict(notification):
        _ = {
            "id": notification.id,
            "title": notification.title,
            "message": notification.message,
            "type": notification.type,
            "is_global": notification.is_global,
            "created_at": str(notification.created_at)
        }
        return _
