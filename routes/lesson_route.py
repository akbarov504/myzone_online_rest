from models import db
from datetime import date
from flask import Blueprint
from models.user import User
from models.lesson import Lesson
from utils.utils import get_response
from utils.decorators import role_required
from models.course_module import CourseModule
from models.lesson_student import LessonStudent
from flask_jwt_extended import get_jwt_identity
from flask_restful import Api, Resource, reqparse
from models.lesson_test_progress import LessonTestProgress

lesson_create_parse = reqparse.RequestParser()
lesson_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
lesson_create_parse.add_argument("description", type=str, required=True, help="Description cannot be blank")
lesson_create_parse.add_argument("video_url", type=str, required=True, help="Video URL cannot be blank")
lesson_create_parse.add_argument("content", type=str, required=True, help="Content cannot be blank")
lesson_create_parse.add_argument("duration", type=str, required=True, help="Duration cannot be blank")
lesson_create_parse.add_argument("order", type=int, required=True, help="Order cannot be blank")
lesson_create_parse.add_argument("cover_url", type=str, required=True, help="Cover URL cannot be blank")

lesson_update_parse = reqparse.RequestParser()
lesson_update_parse.add_argument("course_module_id", type=int)
lesson_update_parse.add_argument("title", type=str)
lesson_update_parse.add_argument("description", type=str)
lesson_update_parse.add_argument("video_url", type=str)
lesson_update_parse.add_argument("content", type=str)
lesson_update_parse.add_argument("duration", type=str)
lesson_update_parse.add_argument("order", type=int)
lesson_update_parse.add_argument("cover_url", type=str)
lesson_update_parse.add_argument("is_active", type=bool)

lesson_bp = Blueprint("lesson", __name__, url_prefix="/api/lesson")
api = Api(lesson_bp)

class LessonResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, lesson_id):
        """Lesson Get API
        Path - /api/lesson/<lesson_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: lesson_id
              in: path
              type: integer
              required: true
              description: Enter Lesson ID
        responses:
            200:
                description: Return a Lesson
            404:
                description: (Lesson not found) or (User not found)
        """
        lesson = Lesson.query.filter_by(id=lesson_id, is_active=True).first()
        if not lesson:
            return get_response("Lesson not found", None, 404), 404

        username = get_jwt_identity()
        found_user = User.query.filter_by(username=username, is_active=True).first()
        if not found_user:
            return get_response("User not found", None, 404), 404
        
        today_date = date.today()
        today_lesson_student = LessonStudent.query.filter_by(student_id=found_user.id, date=today_date).first()
        if today_lesson_student:
            return get_response("You have already accessed lessons today", None, 404), 404
        
        dict_lesson = Lesson.to_dict(lesson)
        lesson_test_progress = LessonTestProgress.query.filter_by(student_id=found_user.id, lesson_id=lesson.id).first()
        
        if not lesson_test_progress:
            dict_lesson_test_progress = None
        else:
            dict_lesson_test_progress = LessonTestProgress.to_dict(lesson_test_progress)

        dict_lesson.update({"lesson_test_progress": dict_lesson_test_progress})
        return get_response("Lesson successfully found", dict_lesson, 200), 200

    @role_required(["ADMIN"])
    def delete(self, lesson_id):
        """Lesson Delete API
        Path - /api/lesson/<lesson_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: lesson_id
              in: path
              type: integer
              required: true
              description: Enter Lesson ID
        responses:
            200:
                description: Delete a Lesson
            404:
                description: Lesson not found
        """
        lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not lesson:
            return get_response("Lesson not found", None, 404), 404

        db.session.delete(lesson)
        db.session.commit()
        return get_response("Successfully deleted lesson", None, 200), 200

    @role_required(["ADMIN"])
    def patch(self, lesson_id):
        """Lesson Update API
        Path - /api/lesson/<lesson_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: lesson_id
              in: path
              type: integer
              required: true
              description: Enter Lesson ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    course_module_id:
                        type: integer
                    title:
                        type: string
                    description:
                        type: string
                    video_url:
                        type: string
                    content:
                        type: string
                    duration:
                        type: string
                    order:
                        type: integer
                    cover_url:
                        type: string
                    is_active:
                        type: boolean
        responses:
            200:
                description: Successfully updated lesson
            404:
                description: Lesson not found
        """
        found_lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not found_lesson:
            return get_response("Lesson not found", None, 404), 404

        data = lesson_update_parse.parse_args()
        course_module_id = data.get('course_module_id', None)
        title = data.get('title', None)
        description = data.get('description', None)
        video_url = data.get('video_url', None)
        content = data.get('content', None)
        duration = data.get('duration', None)
        order = data.get('order', None)
        cover_url = data.get('cover_url', None)
        is_active = data.get('is_active', None)

        if course_module_id is not None:
            found_lesson.course_module_id = course_module_id
        if title is not None:
            found_lesson.title = title
        if description is not None:
            found_lesson.description = description
        if video_url is not None:
            found_lesson.video_url = video_url
        if content is not None:
            found_lesson.content = content
        if duration is not None:
            found_lesson.duration = duration
        if order is not None:
            found_lesson.order = order
        if cover_url is not None:
            found_lesson.cover_url = cover_url
        if is_active is not None:
            found_lesson.is_active = is_active

        db.session.commit()
        return get_response("Successfully updated lesson", None, 200), 200

class LessonListCreateResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, course_module_id):
        """Lesson List API
        Path - /api/lesson/course_module/<course_module_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: course_module_id
              in: path
              type: integer
              required: true
              description: Enter Course Module ID

        responses:
            200:
                description: Return Lesson List
            404:
                description: (Course Module not found) or (User not found)
        """
        found_course_module = CourseModule.query.filter_by(id=course_module_id).first()
        if not found_course_module:
            return get_response("Course Module not found", None, 404), 404

        lesson_list = Lesson.query.filter_by(course_module_id=found_course_module.id).order_by(Lesson.order.asc()).all()
        result_lesson_list = []

        username = get_jwt_identity()
        found_user = User.query.filter_by(username=username, is_active=True).first()
        if not found_user:
            return get_response("User not found", None, 404), 404
        
        today_date = date.today()
        today_lesson_student = LessonStudent.query.filter_by(student_id=found_user.id, date=today_date).first()
        if today_lesson_student:
            return get_response("You have already accessed lessons today", None, 404), 404

        for lesson in lesson_list:
            dict_lesson = Lesson.to_dict(lesson)

            lesson_test_progress = LessonTestProgress.query.filter_by(student_id=found_user.id, lesson_id=lesson.id).first()

            if not lesson_test_progress:
                dict_lesson_test_progress = None
            else:
                dict_lesson_test_progress = LessonTestProgress.to_dict(lesson_test_progress)

            dict_lesson.update({"lesson_test_progress": dict_lesson_test_progress})
            result_lesson_list.append(dict_lesson)

        return get_response("Lesson List", result_lesson_list, 200), 200

    @role_required(["ADMIN"])
    def post(self, course_module_id):
        """Lesson Create API
        Path - /api/lesson/course_module/<course_module_id>
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: course_module_id
              in: path
              type: integer
              required: true
              description: Enter Course Module ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    title: 
                        type: string
                    description:
                        type: string
                    video_url:
                        type: string
                    content:
                        type: string
                    duration:
                        type: string
                    order:
                        type: integer
                    cover_url:
                        type: string
                required: [title, description, video_url, content, duration, order, cover_url]
        responses:
            200:
                description: Return New Lesson ID
            400:
                description: (Title, Description, Video URL, Content, Duration, Order or Cover URL is Blank) or (Lesson with this Title already exists)
            404:
                description: Course Module not found
        """
        data = lesson_create_parse.parse_args()
        title = data['title']
        description = data['description']
        video_url = data['video_url']
        content = data['content']
        duration = data['duration']
        order = data['order']
        cover_url = data['cover_url']

        found_course_module = CourseModule.query.filter_by(id=course_module_id).first()
        if not found_course_module:
            return get_response("Course Module not found", None, 404), 404

        lesson = Lesson.query.filter_by(title=title, course_module_id=found_course_module.id).first()
        if lesson:
            return get_response("Lesson Title already exists", None, 400), 400
        
        new_lesson = Lesson(found_course_module.id, title, description, video_url, content, duration, order, cover_url)
        db.session.add(new_lesson)
        db.session.commit()
        return get_response("Successfully created lesson", new_lesson.id, 200), 200

api.add_resource(LessonResource, "/<lesson_id>")
api.add_resource(LessonListCreateResource, "/course_module/<course_module_id>")
