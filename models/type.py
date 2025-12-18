import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class Type(db.Model):
    __tablename__ = "type"

    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, title, description):
        super().__init__()
        self.title = title
        self.description = description
    
    @staticmethod
    def to_dict(type):
        _ = {
            "id": type.id,
            "title": type.title,
            "description": type.description,
            "created_at": str(type.created_at)
        }
        return _
