import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class LessonStudent(db.Model):
    __tablename__ = "lesson_student"

    id = db.Column(db.Integer(), primary_key=True)

    student_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, student_id, date):
        super().__init__()
        self.student_id = student_id
        self.date = date
    
    @staticmethod
    def to_dict(lesson_student):
        _ = {
            "id": lesson_student.id,
            "student_id": lesson_student.student_id,
            "date": str(lesson_student.date),
            "created_at": str(lesson_student.created_at)
        }
        return _
