import pytz, uuid
from models import db
from pathlib import Path
from flask import Blueprint
from models.user import User
from models.course import Course
from utils.utils import get_response
from flask_restful import Api, Resource
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from models.meeting_lesson import MeetingLesson

from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

time_zone = pytz.timezone("Asia/Tashkent")

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = Path(__file__).parent.parent.joinpath("service_account.json")

credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject="info@myzone-edu.uz")
service = build('calendar', 'v3', credentials=credentials)

meeting_lesson_bp = Blueprint("meeting_lesson", __name__, url_prefix="/api/meeting_lesson")
api = Api(meeting_lesson_bp)

class MeetingLessonResource(Resource):
    decorators = [role_required(["TEACHER", "STUDENT"])]

    def get(self, course_id):
        """Meeting Lesson GET API
        Path - /api/meeting_lesson/<course_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: course_id
              in: path
              type: integer
              required: true
              description: Enter Course ID
        responses:
            200:
                description: (Return a Meeting Lesson) or (No Active Meeting Lesson)
            404:
                description: Course not found
        """
        found_course = Course.query.filter_by(id=course_id, is_active=True).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404

        result_meeting_lesson_list = []
        meeting_lesson_list = MeetingLesson.query.filter_by(course_id=found_course.id, status="ACTIVE").order_by(MeetingLesson.started_at.desc()).all()

        for meeting_lesson in meeting_lesson_list:
            found_teacher = User.query.filter_by(id=meeting_lesson.teacher_id, role="TEACHER", is_active=True).first()

            if found_teacher:
                dict_meeting_lesson = MeetingLesson.to_dict(meeting_lesson)
                dict_found_teacher = User.to_dict(found_teacher)

                dict_meeting_lesson.update({"teacher": dict_found_teacher})
                result_meeting_lesson_list.append(dict_meeting_lesson)
            else:
                dict_meeting_lesson = MeetingLesson.to_dict(meeting_lesson)
                dict_meeting_lesson.update({"teacher": None})
                result_meeting_lesson_list.append(dict_meeting_lesson)

        return get_response("Active Meeting Lesson found", result_meeting_lesson_list, 200), 200

class MeetingLessonStartResource(Resource):
    decorators = [role_required(["TEACHER"])]

    def post(self, teacher_id, course_id):
        """Meeting Lesson Start POST API
        Path - /api/meeting_lesson/start/<teacher_id>/<course_id>
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: teacher_id
              in: path
              type: integer
              required: true
              description: Enter Teacher ID

            - name: course_id
              in: path
              type: integer
              required: true
              description: Enter Course ID
        responses:
            200:
                description: Return a new Meeting Lesson
            400:
                description: Active meeting already exists
            404:
                description: (Teacher not found) or (Course not found)
        """
        found_teacher = User.query.filter_by(id=teacher_id, role="TEACHER", is_active=True).first()
        if not found_teacher:
            return get_response("Teacher not found", None, 404), 404

        found_course = Course.query.filter_by(id=course_id, is_active=True).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404
        
        found_meeting_lesson = MeetingLesson.query.filter_by(teacher_id=found_teacher.id, course_id=found_course.id, status="ACTIVE").first()
        if found_meeting_lesson:
            return get_response("Active meeting already exists", None, 400), 400
        
        meeting_id = str(uuid.uuid4())
        start_time = datetime.now(time_zone)
        end_time = datetime.now(time_zone) + timedelta(hours=6)

        event = {
            'summary': 'Online dars',
            'description': 'Avtomatik yaratilgan online darsi',
            'start': {
                'dateTime': f'{start_time.isoformat()}',
                'timeZone': 'Asia/Tashkent',
            },
            'end': {
                'dateTime': f'{end_time.isoformat()}',
                'timeZone': 'Asia/Tashkent',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f'{meeting_id}'
                }
            }
        }

        created_event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
        calendar_event_id = created_event["id"]
        meet_link = created_event['hangoutLink']

        new_meeting_lesson = MeetingLesson(found_teacher.id, found_course.id, meet_link, "ACTIVE", start_time, end_time, calendar_event_id)
        db.session.add(new_meeting_lesson)
        db.session.commit()

        return get_response("Successfully create Meeting Lesson", MeetingLesson.to_dict(new_meeting_lesson), 200), 200

class MeetingLessonFinishResource(Resource):
    decorators = [role_required(["TEACHER"])]

    def post(self, meeting_lesson_id):
        """Meeting Lesson Finish POST API
        Path - /api/meeting_lesson/finish/<meeting_lesson_id>
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: meeting_lesson_id
              in: path
              type: integer
              required: true
              description: Enter Meeting Lesson ID
        responses:
            200:
                description: Finish Meeting Lesson
            403:
                description: Permission denied
            404:
                description: (Meeting Lesson not found) or (Teacher not found)
        """
        username = get_jwt_identity()

        found_teacher = User.query.filter_by(username=username, is_active=True).first()
        if not found_teacher:
            return get_response("Teacher not found", None, 404), 404

        found_meeting_lesson = MeetingLesson.query.filter_by(id=meeting_lesson_id, status="ACTIVE").first()
        if not found_meeting_lesson:
            return get_response("Meeting Lesson not found", None, 404), 404
        
        if found_meeting_lesson.teacher_id != found_teacher.id:
            return get_response("Permission denied", None, 403), 403
        
        found_meeting_lesson.status = "FINISHED"
        found_meeting_lesson.ended_at = datetime.now(time_zone)

        db.session.commit()
        return get_response("Successfully finish Meeting Lesson", None, 200), 200

api.add_resource(MeetingLessonResource, "/<course_id>")
api.add_resource(MeetingLessonStartResource, "/start/<teacher_id>/<course_id>")
api.add_resource(MeetingLessonFinishResource, "/finish/<meeting_lesson_id>")
