import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class CourseModule(db.Model):
    __tablename__ = "course_module"

    id = db.Column(db.Integer(), primary_key=True)

    course_id = db.Column(db.Integer(), db.ForeignKey("course.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    order = db.Column(db.Integer(), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, course_id, title, description, order):
        super().__init__()
        self.course_id = course_id
        self.title = title
        self.description = description
        self.order = order
    
    @staticmethod
    def to_dict(course_module):
        _ = {
            "id": course_module.id,
            "course_id": course_module.course_id,
            "title": course_module.title,
            "description": course_module.description,
            "order": course_module.order,
            "is_active": course_module.is_active,
            "created_at": str(course_module.created_at)
        }
        return _
