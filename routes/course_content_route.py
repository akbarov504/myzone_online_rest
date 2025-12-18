from models import db
from flask import Blueprint
from models.course import Course
from utils.utils import get_response
from utils.decorators import role_required
from models.course_content import CourseContent
from flask_restful import Api, Resource, reqparse

course_content_create_parse = reqparse.RequestParser()
course_content_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
course_content_create_parse.add_argument("description", type=str, required=True, help="Description cannot be blank")
course_content_create_parse.add_argument("content_url", type=str, required=True, help="Content URL cannot be blank")

course_content_update_parse = reqparse.RequestParser()
course_content_update_parse.add_argument("course_id", type=int)
course_content_update_parse.add_argument("title", type=str)
course_content_update_parse.add_argument("description", type=str)
course_content_update_parse.add_argument("content_url", type=str)

course_content_bp = Blueprint("course_content", __name__, url_prefix="/api/course_content")
api = Api(course_content_bp)

class CourseContentResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, course_content_id):
        """Course Content Get API
        Path - /api/course_content/<course_content_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: course_content_id
              in: path
              type: integer
              required: true
              description: Enter Course Content ID
        responses:
            200:
                description: Return a Course Content
            404:
                description: Course Content not found
        """
        course_content = CourseContent.query.filter_by(id=course_content_id).first()
        if not course_content:
            return get_response("Course Content not found", None, 404), 404

        return get_response("Course Content successfully found", CourseContent.to_dict(course_content), 200), 200

    @role_required(["ADMIN"])
    def delete(self, course_content_id):
        """Course Content Delete API
        Path - /api/course_content/<course_content_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: course_content_id
              in: path
              type: integer
              required: true
              description: Enter Course Content ID
        responses:
            200:
                description: Delete a Course Content
            404:
                description: Course Content not found
        """
        course_content = CourseContent.query.filter_by(id=course_content_id).first()
        if not course_content:
            return get_response("Course Content not found", None, 404), 404

        db.session.delete(course_content)
        db.session.commit()
        return get_response("Successfully deleted course content", None, 200), 200

    @role_required(["ADMIN"])
    def patch(self, course_content_id):
        """Course Content Update API
        Path - /api/course_content/<course_content_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: course_content_id
              in: path
              type: integer
              required: true
              description: Enter Course Content ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    course_id:
                        type: integer
                    title:
                        type: string
                    description:
                        type: string
                    content_url:
                        type: string
        responses:
            200:
                description: Successfully updated course content
            404:
                description: Course Content not found
        """
        found_course_content = CourseContent.query.filter_by(id=course_content_id).first()
        if not found_course_content:
            return get_response("Course Content not found", None, 404), 404

        data = course_content_update_parse.parse_args()
        course_id = data.get('course_id', None)
        title = data.get('title', None)
        description = data.get('description', None)
        content_url = data.get('content_url', None)

        if course_id is not None:
            found_course_content.course_id = course_id
        if title is not None:
            found_course_content.title = title
        if description is not None:
            found_course_content.description = description
        if content_url is not None:
            found_course_content.content_url = content_url

        db.session.commit()
        return get_response("Successfully updated course content", None, 200), 200

class CourseContentListCreateResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, course_id):
        """Course Content List API
        Path - /api/course_content/course/<course_id>
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
                description: Return Course Content List
            404:
                description: Course not found
        """
        found_course = Course.query.filter_by(id=course_id).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404

        course_content_list = CourseContent.query.filter_by(course_id=found_course.id).order_by(CourseContent.created_at.desc()).all()
        result_course_content_list = [CourseContent.to_dict(course_content) for course_content in course_content_list]
        return get_response("Course Content List", result_course_content_list, 200), 200

    @role_required(["ADMIN"])
    def post(self, course_id):
        """Course Content Create API
        Path - /api/course_content/course/<course_id>
        Method - POST
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
                    content_url:
                        type: string
                required: [title, description, content_url]
        responses:
            200:
                description: Return New Course Content ID
            400:
                description: (Title, Description, Content URL is Blank) or (Course Content with this Title already exists)
            404:
                description: Course not found
        """
        data = course_content_create_parse.parse_args()
        title = data['title']
        description = data['description']
        content_url = data['content_url']

        found_course = Course.query.filter_by(id=course_id).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404

        course_content = CourseContent.query.filter_by(title=title, course_id=found_course.id).first()
        if course_content:
            return get_response("Course Content Title already exists", None, 400), 400
        
        new_course_content = CourseContent(found_course.id, title, description, content_url)
        db.session.add(new_course_content)
        db.session.commit()
        return get_response("Successfully created course content", new_course_content.id, 200), 200

api.add_resource(CourseContentResource, "/<course_content_id>")
api.add_resource(CourseContentListCreateResource, "/course/<course_id>")
