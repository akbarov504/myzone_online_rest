from models import db
from flask import Blueprint
from datetime import timedelta
from models.lesson import Lesson
from models.course import Course
from utils.utils import get_response
from utils.decorators import role_required
from models.course_module import CourseModule
from models.course_content import CourseContent
from flask_restful import Api, Resource, reqparse

course_create_parse = reqparse.RequestParser()
course_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
course_create_parse.add_argument("description", type=str, required=True, help="Description cannot be blank")
course_create_parse.add_argument("image_url", type=str, required=True, help="Image URL cannot be blank")
course_create_parse.add_argument("level", type=str, required=True, help="Level cannot be blank")
course_create_parse.add_argument("type_id", type=int, required=True, help="Type ID cannot be blank")

course_update_parse = reqparse.RequestParser()
course_update_parse.add_argument("title", type=str)
course_update_parse.add_argument("description", type=str)
course_update_parse.add_argument("image_url", type=str)
course_update_parse.add_argument("level", type=str)
course_create_parse.add_argument("type_id", type=int)
course_update_parse.add_argument("is_active", type=bool)

course_bp = Blueprint("course", __name__, url_prefix="/api/course")
api = Api(course_bp)

class CourseResource(Resource):

    @role_required(["ADMIN", "TEACHER", "STUDENT"])
    def get(self, course_id):
        """Course Get API
        Path - /api/course/<course_id>
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
                description: Return a Course
            404:
                description: Course not found
        """
        course = Course.query.filter_by(id=course_id, is_active=True).first()
        if not course:
            return get_response("Course not found", None, 404), 404
        
        return get_response("Course successfully found", Course.to_dict(course), 200), 200

    @role_required(["ADMIN"])
    def delete(self, course_id):
        """Course Delete API
        Path - /api/course/<course_id>
        Method - DELETE
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
                description: Delete a Course
            404:
                description: Course not found
        """
        course = Course.query.filter_by(id=course_id).first()
        if not course:
            return get_response("Course not found", None, 404), 404

        db.session.delete(course)
        db.session.commit()
        return get_response("Successfully deleted course", None, 200), 200

    @role_required(["ADMIN"])
    def patch(self, course_id):
        """Course Update API
        Path - /api/course/<course_id>
        Method - PATCH
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
                    image_url:
                        type: string
                    level:
                        type: string
                    type_id:
                        type: integer
                    is_active:
                        type: boolean
        responses:
            200:
                description: Successfully updated course
            404:
                description: Course not found
        """
        found_course = Course.query.filter_by(id=course_id).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404
        
        data = course_update_parse.parse_args()
        title = data.get('title', None)
        description = data.get('description', None)
        image_url = data.get('image_url', None)
        level = data.get('level', None)
        type_id = data.get('type_id', None)
        is_active = data.get('is_active', None)

        if title is not None:
            found_course.title = title
        if description is not None:
            found_course.description = description
        if image_url is not None:
            found_course.image_url = image_url
        if level is not None:
            found_course.level = level
        if type_id is not None:
            found_course.type_id = type_id
        if is_active is not None:
            found_course.is_active = is_active

        db.session.commit()
        return get_response("Successfully updated course", None, 200), 200

class CourseListCreateResource(Resource):

    @role_required(["ADMIN", "TEACHER", "STUDENT"])
    def get(self):
        """Course List API
        Path - /api/course
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

        responses:
            200:
                description: Return Course List
        """
        course_list = Course.query.filter_by().order_by(Course.created_at.desc()).all()
        result_course_list = [Course.to_dict(course) for course in course_list]
        return get_response("Course List", result_course_list, 200), 200

    @role_required(["ADMIN"])
    def post(self):
        """Course Create API
        Path - /api/course
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

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
                    image_url:
                        type: string
                    level:
                        type: string
                    type_id:
                        type: integer
                required: [title, description, image_url, level, type_id]
        responses:
            200:
                description: Return New Course ID
            400:
                description: (Title, Description, Image URL, Level or Type ID is Blank) or (Course with this Title already exists)
        """
        data = course_create_parse.parse_args()
        title = data['title']
        description = data['description']
        image_url = data['image_url']
        level = data['level']
        type_id = data['type_id']

        course = Course.query.filter_by(title=title).first()
        if course:
            return get_response("Course Title already exists", None, 400), 400
        
        new_course = Course(title, description, image_url, level, type_id)
        db.session.add(new_course)
        db.session.commit()
        return get_response("Successfully created course", new_course.id, 200), 200

class CourseCountsResource(Resource):
    decorators = [role_required(["ADMIN", "STUDENT"])]

    def get(self, course_id):
        """Course Counts Get API
        Path - /api/course/counts/<course_id>
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
                description: Return a Course Counts
            404:
                description: Course not found
        """
        found_course = Course.query.filter_by(id=course_id, is_active=True).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404
        
        lesson_count = 0
        total_duration = timedelta()
        course_module_list = CourseModule.query.filter_by(course_id=found_course.id, is_active=True).all()
        course_content_list = CourseContent.query.filter_by(course_id=found_course.id).all()

        for course_module in course_module_list:
            lesson_list = Lesson.query.filter_by(course_module_id=course_module.id, is_active=True).all()
            for lesson in lesson_list:
                m, s = map(int, lesson.duration.split(":"))
                total_duration += timedelta(minutes=m, seconds=s)
            lesson_count += len(lesson_list)

        result = {
            "course_module_count": len(course_module_list),
            "course_content_count": len(course_content_list),
            "lesson_count": lesson_count,
            "lesson_total_duration": str(total_duration)
        }
        return get_response("Course counts successfully found", result, 200), 200

api.add_resource(CourseResource, "/<course_id>")
api.add_resource(CourseListCreateResource, "/")
api.add_resource(CourseCountsResource, "/counts/<course_id>")
