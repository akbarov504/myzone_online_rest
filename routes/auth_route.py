from flask import Blueprint
from models.user import User
from utils.utils import get_response
from flask_bcrypt import check_password_hash
from flask_restful import Api, Resource, reqparse
from flask_jwt_extended import create_access_token

auth_parse = reqparse.RequestParser()
auth_parse.add_argument("username", type=str, required=True, help="Username cannot be blank")
auth_parse.add_argument("password", type=str, required=True, help="Password cannot be blank")

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
api = Api(auth_bp)

class AuthResource(Resource):

    def post(self):
        """Auth Login API
        Path - /api/auth/login
        Method - POST
        ---
        consumes: application/json
        parameters:
            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    username: 
                        type: string
                    password:
                        type: string
                required: [username, password]
        responses:
            200:
                description: Return Access Token
            404:
                description: Username or Password is Incorrect
            400:
                description: Username or Password is Blank
        """
        data = auth_parse.parse_args()
        username = data['username']
        password = data['password']

        user = User.query.filter_by(username=username, is_active=True).first()
        if not user:
            return get_response("Username or Password is incorrect", None, 404), 404
        
        if not check_password_hash(user.password, password):
            return get_response("Username or Password is incorrect", None, 404), 404
        
        access_token = create_access_token(identity=user.username)
        result_data = {
            "full_name": user.full_name,
            "user_id": user.id,
            "role": user.role,
            "type_id": user.type_id,
            "access_token": access_token
        }
        return get_response("Successfully Logged in!", result_data, 200), 200

api.add_resource(AuthResource, "/login")
