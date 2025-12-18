import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class CourseSave(db.Model):
    __tablename__ = "course_save"

    id = db.Column(db.Integer(), primary_key=True)

    course_id = db.Column(db.Integer(), db.ForeignKey("course.id"), nullable=False)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, course_id, user_id):
        super().__init__()
        self.course_id = course_id
        self.user_id = user_id
    
    @staticmethod
    def to_dict(course_save):
        _ = {
            "id": course_save.id,
            "course_id": course_save.course_id,
            "user_id": course_save.user_id,
            "created_at": str(course_save.created_at)
        }
        return _
