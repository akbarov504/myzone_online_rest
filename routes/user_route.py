from models import db
from flask import Blueprint
from models.user import User
from models.course import Course
from models.lesson import Lesson
from utils.utils import get_response
from utils.decorators import role_required
from models.course_module import CourseModule
from flask_bcrypt import generate_password_hash
from flask_restful import Api, Resource, reqparse
from models.lesson_test_progress import LessonTestProgress

user_create_parse = reqparse.RequestParser()
user_create_parse.add_argument("full_name", type=str, required=True, help="Full Name cannot be blank")
user_create_parse.add_argument("phone_number", type=str, required=True, help="Phone Number cannot be blank")
user_create_parse.add_argument("username", type=str, required=True, help="Username cannot be blank")
user_create_parse.add_argument("password", type=str, required=True, help="Password cannot be blank")
user_create_parse.add_argument("role", type=str, required=True, help="Role cannot be blank")
user_create_parse.add_argument("active_term", type=int, required=True, help="Active Term cannot be blank")
user_create_parse.add_argument("type_id", type=int, required=True, help="Type ID cannot be blank")

user_update_parse = reqparse.RequestParser()
user_update_parse.add_argument("full_name", type=str)
user_update_parse.add_argument("phone_number", type=str)
user_update_parse.add_argument("username", type=str)
user_update_parse.add_argument("password", type=str)
user_update_parse.add_argument("role", type=str)
user_update_parse.add_argument("active_term", type=int)
user_update_parse.add_argument("type_id", type=int)
user_update_parse.add_argument("is_active", type=bool)

user_bp = Blueprint("user", __name__, url_prefix="/api/user")
api = Api(user_bp)

class UserResource(Resource):    

    @role_required(["ADMIN", "TEACHER", "STUDENT", "SUPPORT"])
    def get(self, user_id):
        """User Get API
        Path - /api/user/<user_id>
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
                description: Return a User
            404:
                description: User not found
        """
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return get_response("User not found", None, 404), 404
        
        return get_response("User successfully found", User.to_dict(user), 200), 200

    @role_required(["ADMIN"])
    def delete(self, user_id):
        """User Delete API
        Path - /api/user/<user_id>
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
        responses:
            200:
                description: Delete a User
            404:
                description: User not found
        """
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return get_response("User not found", None, 404), 404
        
        db.session.delete(user)
        db.session.commit()
        return get_response("Successfully deleted user", None, 200), 200
    
    @role_required(["ADMIN"])
    def patch(self, user_id):
        """User Update API
        Path - /api/user/<user_id>
        Method - PATCH
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
                    full_name: 
                        type: string
                    phone_number:
                        type: string
                    username:
                        type: string
                    password:
                        type: string
                    role:
                        type: string
                    active_term:
                        type: integer
                    type_id:
                        type: integer
                    is_active:
                        type: boolean
        responses:
            200:
                description: Successfully updated user
            404:
                description: User not found
        """
        found_user = User.query.filter_by(id=user_id).first()
        if not found_user:
            return get_response("User not found", None, 404), 404
        
        data = user_update_parse.parse_args()
        full_name = data.get('full_name', None)
        phone_number = data.get('phone_number', None)
        username = data.get('username', None)
        password = data.get('password', None)
        role = data.get('role', None)
        active_term = data.get('active_term', None)
        type_id = data.get('type_id', None)
        is_active = data.get('is_active', None)

        if full_name is not None:
            found_user.full_name = full_name
        if phone_number is not None:
            found_user.phone_number = phone_number
        if username is not None:
            found_user.username = username
        if password is not None:
            found_user.password = generate_password_hash(password).decode("utf-8")
        if role is not None:
            found_user.role = role
        if active_term is not None:
            found_user.active_term = active_term
        if type_id is not None:
            found_user.type_id = type_id
        if is_active is not None:
            found_user.is_active = is_active

        db.session.commit()
        return get_response("Successfully updated user", None, 200), 200

class UserListCreateResource(Resource):
    decorators = [role_required(["ADMIN", "SUPPORT"])]

    def get(self):
        """Student List API
        Path - /api/user
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
                description: Return Student List
        """
        user_list = User.query.order_by(User.created_at.desc()).all()
        result_user_list = [User.to_dict(user) for user in user_list]
        return get_response("Student List", result_user_list, 200), 200

    def post(self):
        """User Create API
        Path - /api/user
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
                    full_name: 
                        type: string
                    phone_number:
                        type: string
                    username:
                        type: string
                    password:
                        type: string
                    role:
                        type: string
                    active_term:
                        type: integer
                    type_id:
                        type: integer
                required: [full_name, phone_number, username, password, role, active_term, type_id]
        responses:
            200:
                description: Return New User ID
            400:
                description: (Full Name, Phone Number, Username, Password, Role, Active Term or Type ID is Blank) or (Phone Number already taken or Username already taken)
        """
        data = user_create_parse.parse_args()
        full_name = data['full_name']
        phone_number = data['phone_number']
        username = data['username']
        password = data['password']
        role = data['role']
        active_term = data['active_term']
        type_id = data['type_id']

        user = User.query.filter_by(phone_number=phone_number).first()
        if user:
            return get_response("Phone Number already exists", None, 400), 400
        
        user = User.query.filter_by(username=username).first()
        if user:
            return get_response("Username already exists", None, 400), 400
    
        new_user = User(full_name, phone_number, username, password, role, active_term, type_id)
        db.session.add(new_user)
        db.session.commit()

        if role == "STUDENT":
            course_list = Course.query.filter_by(type_id=type_id, is_active=True).all()
            for course in course_list:
                course_module = CourseModule.query.filter_by(course_id=course.id, order=1, is_active=True).first()
                lesson = Lesson.query.filter_by(course_module_id=course_module.id, order=1, is_active=True).first()

                new_lesson_test_progress = LessonTestProgress(new_user.id, lesson.id, False, 0)
                db.session.add(new_lesson_test_progress)
                
            db.session.commit()

        return get_response("Successfully created user", new_user.id, 200), 200

api.add_resource(UserResource, "/<user_id>")
api.add_resource(UserListCreateResource, "/")
