import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class LessonTestProgress(db.Model):
    __tablename__ = "lesson_test_progress"

    id = db.Column(db.Integer(), primary_key=True)

    student_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    lesson_id = db.Column(db.Integer(), db.ForeignKey("lesson.id"), nullable=False)
    is_completed = db.Column(db.Boolean(), nullable=False)
    best_score = db.Column(db.Float(), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, student_id, lesson_id, is_completed, best_score):
        super().__init__()
        self.student_id = student_id
        self.lesson_id = lesson_id
        self.is_completed = is_completed
        self.best_score = best_score
    
    @staticmethod
    def to_dict(lesson_test_progress):
        _ = {
            "id": lesson_test_progress.id,
            "student_id": lesson_test_progress.student_id,
            "lesson_id": lesson_test_progress.lesson_id,
            "is_completed": lesson_test_progress.is_completed,
            "best_score": lesson_test_progress.best_score,
            "created_at": str(lesson_test_progress.created_at)
        }
        return _
