import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class CourseContent(db.Model):
    __tablename__ = "course_content"

    id = db.Column(db.Integer(), primary_key=True)

    course_id = db.Column(db.Integer(), db.ForeignKey("course.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    content_url = db.Column(db.Text(), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, course_id, title, description, content_url):
        super().__init__()
        self.course_id = course_id
        self.title = title
        self.description = description
        self.content_url = content_url
    
    @staticmethod
    def to_dict(course_content):
        _ = {
            "id": course_content.id,
            "course_id": course_content.course_id,
            "title": course_content.title,
            "description": course_content.description,
            "content_url": course_content.content_url,
            "created_at": str(course_content.created_at)
        }
        return _
