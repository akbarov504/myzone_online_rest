import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class LessonTest(db.Model):
    __tablename__ = "lesson_test"

    id = db.Column(db.Integer(), primary_key=True)

    lesson_id = db.Column(db.Integer(), db.ForeignKey("lesson.id"), nullable=False)
    question_text = db.Column(db.Text(), nullable=False)
    option_a = db.Column(db.Text(), nullable=False)
    option_b = db.Column(db.Text(), nullable=False)
    option_c = db.Column(db.Text(), nullable=False)
    option_d = db.Column(db.Text(), nullable=False)
    correct_option = db.Column(db.String(10), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, lesson_id, question_text, option_a, option_b, option_c, option_d, correct_option):
        super().__init__()
        self.lesson_id = lesson_id
        self.question_text = question_text
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d
        self.correct_option = correct_option
    
    @staticmethod
    def to_dict(lesson_test):
        _ = {
            "id": lesson_test.id,
            "lesson_id": lesson_test.lesson_id,
            "question_text": lesson_test.question_text,
            "option_a": lesson_test.option_a,
            "option_b": lesson_test.option_b,
            "option_c": lesson_test.option_c,
            "option_d": lesson_test.option_d,
            "correct_option": lesson_test.correct_option,
            "created_at": str(lesson_test.created_at)
        }
        return _
