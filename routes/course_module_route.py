from models import db
from flask import Blueprint
from models.course import Course
from utils.utils import get_response
from utils.decorators import role_required
from models.course_module import CourseModule
from flask_restful import Api, Resource, reqparse

course_module_create_parse = reqparse.RequestParser()
course_module_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
course_module_create_parse.add_argument("description", type=str, required=True, help="Description cannot be blank")
course_module_create_parse.add_argument("order", type=int, required=True, help="Order cannot be blank")

course_module_update_parse = reqparse.RequestParser()
course_module_update_parse.add_argument("course_id", type=int)
course_module_update_parse.add_argument("title", type=str)
course_module_update_parse.add_argument("description", type=str)
course_module_update_parse.add_argument("order", type=int)
course_module_update_parse.add_argument("is_active", type=bool)

course_module_bp = Blueprint("course_module", __name__, url_prefix="/api/course_module")
api = Api(course_module_bp)

class CourseModuleResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, course_module_id):
        """Course Module Get API
        Path - /api/course_module/<course_module_id>
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
                description: Return a Course Module
            404:
                description: Course Module not found
        """
        course_module = CourseModule.query.filter_by(id=course_module_id, is_active=True).first()
        if not course_module:
            return get_response("Course Module Not found", None, 404), 404

        return get_response("Course Module successfully found", CourseModule.to_dict(course_module), 200), 200

    @role_required(["ADMIN"])
    def delete(self, course_module_id):
        """Course Module Delete API
        Path - /api/course_module/<course_module_id>
        Method - DELETE
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
                description: Delete a Course Module
            404:
                description: Course Module not found
        """
        course_module = CourseModule.query.filter_by(id=course_module_id).first()
        if not course_module:
            return get_response("Course Module Not found", None, 404), 404

        db.session.delete(course_module)
        db.session.commit()
        return get_response("Successfully deleted course module", None, 200), 200

    @role_required(["ADMIN"])
    def patch(self, course_module_id):
        """Course Module Update API
        Path - /api/course_module/<course_module_id>
        Method - PATCH
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
                    course_id:
                        type: integer
                    title:
                        type: string
                    description:
                        type: string
                    order:
                        type: integer
                    is_active:
                        type: boolean
        responses:
            200:
                description: Successfully updated course module
            404:
                description: Course Module Not found
        """
        found_course_module = CourseModule.query.filter_by(id=course_module_id).first()
        if not found_course_module:
            return get_response("Course Module Not found", None, 404), 404

        data = course_module_update_parse.parse_args()
        course_id = data.get('course_id', None)
        title = data.get('title', None)
        description = data.get('description', None)
        order = data.get('order', None)
        is_active = data.get('is_active', None)

        if course_id is not None:
            found_course_module.course_id = course_id
        if title is not None:
            found_course_module.title = title
        if description is not None:
            found_course_module.description = description
        if order is not None:
            found_course_module.order = order
        if is_active is not None:
            found_course_module.is_active = is_active

        db.session.commit()
        return get_response("Successfully updated course module", None, 200), 200

class CourseModuleListCreateResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, course_id):
        """Course Module List API
        Path - /api/course_module/course/<course_id>
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
                description: Return Course Module List
            404:
                description: Course not found
        """
        found_course = Course.query.filter_by(id=course_id).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404

        course_module_list = CourseModule.query.filter_by(course_id=found_course.id).order_by(CourseModule.created_at.desc()).all()
        result_course_module_list = [CourseModule.to_dict(course_module) for course_module in course_module_list]
        return get_response("Course Module List", result_course_module_list, 200), 200

    @role_required(["ADMIN"])
    def post(self, course_id):
        """Course Module Create API
        Path - /api/course_module/course/<course_id>
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
                    order:
                        type: integer
                required: [title, description, order]
        responses:
            200:
                description: Return New Course Module ID
            400:
                description: (Title, Description, Order is Blank) or (Course Module with this Title already exists)
            404:
                description: Course not found
        """
        data = course_module_create_parse.parse_args()
        title = data['title']
        description = data['description']
        order = data['order']

        found_course = Course.query.filter_by(id=course_id).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404

        course_module = CourseModule.query.filter_by(title=title, course_id=found_course.id).first()
        if course_module:
            return get_response("Course Module Title already exists", None, 400), 400
        
        new_course_module = CourseModule(found_course.id, title, description, order)
        db.session.add(new_course_module)
        db.session.commit()
        return get_response("Successfully created course module", new_course_module.id, 200), 200

api.add_resource(CourseModuleResource, "/<course_module_id>")
api.add_resource(CourseModuleListCreateResource, "/course/<course_id>")
