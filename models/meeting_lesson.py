import pytz
from models import db
from datetime import datetime

time_zone = pytz.timezone("Asia/Tashkent")

class MeetingLesson(db.Model):
    __tablename__ = "meeting_lesson"

    id = db.Column(db.Integer(), primary_key=True)

    teacher_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable=False)
    course_id = db.Column(db.Integer(), db.ForeignKey("course.id"), nullable=False)
    meet_url = db.Column(db.Text(), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    started_at = db.Column(db.DateTime(), nullable=False)
    ended_at = db.Column(db.DateTime(), nullable=False)
    calendar_event_id = db.Column(db.Text(), nullable=False)

    created_at = db.Column(db.DateTime(), default=lambda: datetime.now(time_zone))

    def __init__(self, teacher_id, course_id, meet_url, status, started_at, ended_at, calendar_event_id):
        super().__init__()
        self.teacher_id = teacher_id
        self.course_id = course_id
        self.meet_url = meet_url
        self.status = status
        self.started_at = started_at
        self.ended_at = ended_at
        self.calendar_event_id = calendar_event_id
    
    @staticmethod
    def to_dict(meeting_lesson):
        _ = {
            "id": meeting_lesson.id,
            "teacher_id": meeting_lesson.teacher_id,
            "course_id": meeting_lesson.course_id,
            "meet_url": meeting_lesson.meet_url,
            "status": meeting_lesson.status,
            "started_at": str(meeting_lesson.started_at),
            "ended_at": str(meeting_lesson.ended_at),
            "calendar_event_id": meeting_lesson.calendar_event_id,
            "created_at": str(meeting_lesson.created_at)
        }
        return _
