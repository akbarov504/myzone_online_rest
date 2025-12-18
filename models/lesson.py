import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class Lesson(db.Model):
    __tablename__ = "lesson"

    id = db.Column(db.Integer(), primary_key=True)

    course_module_id = db.Column(db.Integer(), db.ForeignKey("course_module.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text(), nullable=False)
    video_url = db.Column(db.Text(), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    duration = db.Column(db.String(10), nullable=False)
    order = db.Column(db.Integer(), nullable=False)
    cover_url = db.Column(db.Text(), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, course_module_id, title, description, video_url, content, duration, order, cover_url):
        super().__init__()
        self.course_module_id = course_module_id
        self.title = title
        self.description = description
        self.video_url = video_url
        self.content = content
        self.duration = duration
        self.order = order
        self.cover_url = cover_url
    
    @staticmethod
    def to_dict(lesson):
        _ = {
            "id": lesson.id,
            "course_module_id": lesson.course_module_id,
            "title": lesson.title,
            "description": lesson.description,
            "video_url": lesson.video_url,
            "content": lesson.content,
            "duration": lesson.duration,
            "order": lesson.order,
            "cover_url": lesson.cover_url,
            "is_active": lesson.is_active,
            "created_at": str(lesson.created_at)
        }
        return _
