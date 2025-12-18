import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class Course(db.Model):
    __tablename__ = "course"

    id = db.Column(db.Integer(), primary_key=True)

    title = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)
    image_url = db.Column(db.Text(), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    type_id = db.Column(db.Integer(), db.ForeignKey("type.id"), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, title, description, image_url, level, type_id):
        super().__init__()
        self.title = title
        self.description = description
        self.image_url = image_url
        self.level = level
        self.type_id = type_id
    
    @staticmethod
    def to_dict(course):
        _ = {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "image_url": course.image_url,
            "level": course.level,
            "type_id": course.type_id,
            "is_active": course.is_active,
            "created_at": str(course.created_at)
        }
        return _
