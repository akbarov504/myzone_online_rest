import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class ModuleStudent(db.Model):
    __tablename__ = "module_student"

    id = db.Column(db.Integer(), primary_key=True)

    student_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, student_id, date):
        super().__init__()
        self.student_id = student_id
        self.date = date
    
    @staticmethod
    def to_dict(module_student):
        _ = {
            "id": module_student.id,
            "student_id": module_student.student_id,
            "date": str(module_student.date),
            "created_at": str(module_student.created_at)
        }
        return _
