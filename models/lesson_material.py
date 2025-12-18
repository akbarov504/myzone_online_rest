import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class LessonMaterial(db.Model):
    __tablename__ = "lesson_material"

    id = db.Column(db.Integer(), primary_key=True)

    lesson_id = db.Column(db.Integer(), db.ForeignKey("lesson.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    material_url = db.Column(db.Text(), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, lesson_id, title, description, material_url):
        super().__init__()
        self.lesson_id = lesson_id
        self.title = title
        self.description = description
        self.material_url = material_url
    
    @staticmethod
    def to_dict(lesson_material):
        _ = {
            "id": lesson_material.id,
            "lesson_id": lesson_material.lesson_id,
            "title": lesson_material.title,
            "description": lesson_material.description,
            "material_url": lesson_material.material_url,
            "created_at": str(lesson_material.created_at)
        }
        return _
