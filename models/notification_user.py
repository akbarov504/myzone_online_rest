import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class NotificationUser(db.Model):
    __tablename__ = "notification_user"

    id = db.Column(db.Integer(), primary_key=True)

    notification_id = db.Column(db.Integer(), db.ForeignKey("notification.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    is_read = db.Column(db.Boolean(), default=False)
    read_at = db.Column(db.DateTime(), nullable=True)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, notification_id, user_id):
        super().__init__()
        self.notification_id = notification_id
        self.user_id = user_id
    
    @staticmethod
    def to_dict(notification_user):
        _ = {
            "id": notification_user.id,
            "notification_id": notification_user.notification_id,
            "user_id": notification_user.user_id,
            "is_read": notification_user.is_read,
            "read_at": str(notification_user.read_at),
            "created_at": str(notification_user.created_at)
        }
        return _
