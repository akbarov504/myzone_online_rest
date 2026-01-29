import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class SupportTicket(db.Model):
    __tablename__ = "support_ticket"

    id = db.Column(db.Integer(), primary_key=True)

    student_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    
    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))
    updated_at = db.Column(db.DateTime())

    def __init__(self, student_id, status):
        super().__init__()
        self.student_id = student_id
        self.status = status
    
    @staticmethod
    def to_dict(support_ticket):
        _ = {
            "id": support_ticket.id,
            "student_id": support_ticket.student_id,
            "status": support_ticket.status,
            "created_at": str(support_ticket.created_at),
            "updated_at": str(support_ticket.updated_at)
        }
        return _
