from models import db
from flask import Blueprint
from models.user import User
from models.user_payment import UserPayment
from utils.utils import get_response
from utils.decorators import role_required
from flask_restful import Api, Resource, reqparse

user_payment_create_parse = reqparse.RequestParser()
user_payment_create_parse.add_argument("user_id", type=int, required=True, help="User ID cannot be blank")
user_payment_create_parse.add_argument("discount", type=float)
user_payment_create_parse.add_argument("course_price", type=float)

user_payment_update_parse = reqparse.RequestParser()
user_payment_update_parse.add_argument("discount", type=float)
user_payment_update_parse.add_argument("course_price", type=float)

user_payment_bp = Blueprint("user_payment", __name__, url_prefix="/api/user_payment")
api = Api(user_payment_bp)

class UserPaymentResource(Resource):
    decorators = [role_required(["ADMIN", "OPERATOR"])]

    def get(self, user_payment_id):
        """UserPayment Get API
        Path - /api/user_payment/<user_payment_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: user_payment_id
              in: path
              type: integer
              required: true
              description: Enter UserPayment ID
        responses:
            200:
                description: Return a UserPayment
            404:
                description: UserPayment not found
        """
        user_payment = UserPayment.query.filter_by(id=user_payment_id).first()
        if not user_payment:
            return get_response("UserPayment not found", None, 404), 404

        return get_response("UserPayment successfully found", UserPayment.to_dict(user_payment), 200), 200

    def delete(self, user_payment_id):
        """UserPayment Delete API
        Path - /api/user_payment/<user_payment_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: user_payment_id
              in: path
              type: integer
              required: true
              description: Enter UserPayment ID
        responses:
            200:
                description: Delete a UserPayment
            404:
                description: UserPayment not found
        """
        user_payment = UserPayment.query.filter_by(id=user_payment_id).first()
        if not user_payment:
            return get_response("UserPayment not found", None, 404), 404

        db.session.delete(user_payment)
        db.session.commit()
        return get_response("Successfully deleted user payment", None, 200), 200

    def patch(self, user_payment_id):
        """UserPayment Update API
        Path - /api/user_payment/<user_payment_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: user_payment_id
              in: path
              type: integer
              required: true
              description: Enter UserPayment ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    discount:
                        type: number
                    course_price:
                        type: number
        responses:
            200:
                description: Successfully updated user payment
            404:
                description: UserPayment not found
        """
        found_user_payment = UserPayment.query.filter_by(id=user_payment_id).first()
        if not found_user_payment:
            return get_response("UserPayment not found", None, 404), 404

        data = user_payment_update_parse.parse_args()
        discount = data.get("discount", None)
        course_price = data.get("course_price", None)

        if discount is not None:
            found_user_payment.discount = discount
            found_user_payment.course_price = 2_000_000 - (2_000_000 * discount / 100)
        if course_price is not None:
            found_user_payment.course_price = course_price

        db.session.commit()
        return get_response("Successfully updated user payment", None, 200), 200

class UserPaymentListCreateResource(Resource):
    decorators = [role_required(["ADMIN", "OPERATOR"])]

    def get(self):
        """UserPayment List API
        Path - /api/user_payment
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
                description: Return UserPayment List
        """
        user_payment_list = UserPayment.query.order_by(UserPayment.created_at.desc()).all()
        result = [UserPayment.to_dict(up) for up in user_payment_list]
        return get_response("UserPayment List", result, 200), 200

    def post(self):
        """UserPayment Create API
        Path - /api/user_payment
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
                    user_id:
                        type: integer
                    discount:
                        type: number
                    course_price:
                        type: number
                required: [user_id]
        responses:
            200:
                description: Return New UserPayment ID
            400:
                description: UserPayment for this user already exists
            404:
                description: User not found
        """
        data = user_payment_create_parse.parse_args()
        user_id = data["user_id"]
        discount = data.get("discount") or 0
        course_price = data.get("course_price") or 2_000_000

        found_user = User.query.filter_by(id=user_id).first()
        if not found_user:
            return get_response("User not found", None, 404), 404

        existing = UserPayment.query.filter_by(user_id=user_id).first()
        if existing:
            return get_response("UserPayment for this user already exists", None, 400), 400

        new_user_payment = UserPayment(
            user_id=found_user.id,
            full_name=found_user.full_name,
            phone_number=found_user.phone_number,
            username=found_user.username,
            role=found_user.role,
            active_term=found_user.active_term,
            type_id=found_user.type_id,
            is_active=found_user.is_active,
            profile_image=found_user.profile_image,
            discount=discount,
            course_price=course_price,
        )
        db.session.add(new_user_payment)
        db.session.commit()
        return get_response("Successfully created user payment", new_user_payment.id, 200), 200

api.add_resource(UserPaymentResource, "/<user_payment_id>")
api.add_resource(UserPaymentListCreateResource, "/")
