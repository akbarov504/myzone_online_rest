import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class ModuleTest(db.Model):
    __tablename__ = "module_test"

    id = db.Column(db.Integer(), primary_key=True)

    module_id = db.Column(db.Integer(), db.ForeignKey("course_module.id"), nullable=False)
    question_text = db.Column(db.Text(), nullable=False)
    option_a = db.Column(db.Text(), nullable=False)
    option_b = db.Column(db.Text(), nullable=False)
    option_c = db.Column(db.Text(), nullable=False)
    option_d = db.Column(db.Text(), nullable=False)
    correct_option = db.Column(db.String(10), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, module_id, question_text, option_a, option_b, option_c, option_d, correct_option):
        super().__init__()
        self.module_id = module_id
        self.question_text = question_text
        self.option_a = option_a
        self.option_b = option_b
        self.option_c = option_c
        self.option_d = option_d
        self.correct_option = correct_option
    
    @staticmethod
    def to_dict(module_test):
        _ = {
            "id": module_test.id,
            "module_id": module_test.module_id,
            "question_text": module_test.question_text,
            "option_a": module_test.option_a,
            "option_b": module_test.option_b,
            "option_c": module_test.option_c,
            "option_d": module_test.option_d,
            "correct_option": module_test.correct_option,
            "created_at": str(module_test.created_at)
        }
        return _
