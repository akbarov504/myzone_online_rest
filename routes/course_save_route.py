from models import db
from flask import Blueprint
from models.user import User
from models.course import Course
from utils.utils import get_response
from models.course_save import CourseSave
from utils.decorators import role_required
from flask_restful import Api, Resource, reqparse

course_save_parse = reqparse.RequestParser()
course_save_parse.add_argument("course_id", type=int, required=True, help="Course ID cannot be blank")

course_save_bp = Blueprint("course_save", __name__, url_prefix="/api/course_save")
api = Api(course_save_bp)

class CourseSaveResource(Resource):
    decorators = [role_required(["ADMIN", "STUDENT"])]

    def get(self, user_id):
        """Course Save Get API
        Path - /api/course_save/<user_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: user_id
              in: path
              type: integer
              required: true
              description: Enter User ID
        responses:
            200:
                description: Return a Course List
            404:
                description: User not found
        """
        found_user = User.query.filter_by(id=user_id).first()
        if not found_user:
            return get_response("User not found", None, 404), 404

        course_list = []
        course_save_list = CourseSave.query.filter_by(user_id=found_user.id).all()

        for course_save in course_save_list:
            course = Course.query.filter_by(id=course_save.course_id).first()
            if not course:
                continue
            else:
                course_list.append(course)

        result_course_list = [Course.to_dict(course) for course in course_list]
        res = {
            "course_count": len(course_list),
            "course_list": result_course_list
        }
        return get_response("Course Save List successfully found", res, 200), 200

    def delete(self, user_id):
        """Course Save Delete API
        Path - /api/course_save/<user_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: user_id
              in: path
              type: integer
              required: true
              description: Enter User ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    course_id: 
                        type: integer
                required: [course_id]
        responses:
            200:
                description: Delete a Course Save
            400:
                description: Course ID is Blank
            404:
                description: User not found, Course not found, Course Save not found
        """
        data = course_save_parse.parse_args()
        course_id = data['course_id']
        
        found_user = User.query.filter_by(id=user_id).first()
        if not found_user:
            return get_response("User not found", None, 404), 404
        
        found_course = Course.query.filter_by(id=course_id).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404

        course_save = CourseSave.query.filter_by(user_id=found_user.id, course_id=found_course.id).first()
        if not course_save:
            return get_response("Course Save not found", None, 404), 404

        db.session.delete(course_save)
        db.session.commit()
        return get_response("Successfully deleted course save", None, 200), 200

    def post(self, user_id):
        """Course Save Create API
        Path - /api/course_save/<user_id>
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: user_id
              in: path
              type: integer
              required: true
              description: Enter User ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    course_id:
                        type: integer
                required: [course_id]
        responses:
            200:
                description: Return New Course Save ID
            400:
                description: Course ID is Blank
            404:
                description: User not found, Course not found
        """
        data = course_save_parse.parse_args()
        course_id = data['course_id']

        found_user = User.query.filter_by(id=user_id).first()
        if not found_user:
            return get_response("User not found", None, 404), 404
        
        found_course = Course.query.filter_by(id=course_id).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404
        
        found_course_save = CourseSave.query.filter_by(user_id=found_user.id, course_id=found_course.id).first()
        if found_course_save:
            return get_response("Successfully created course save", found_course_save.id, 200), 200
        
        new_course_save = CourseSave(found_course.id, found_user.id)
        db.session.add(new_course_save)
        db.session.commit()
        return get_response("Successfully created course save", new_course_save.id, 200), 200

api.add_resource(CourseSaveResource, "/<user_id>")
