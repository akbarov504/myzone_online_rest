from models import db
from flask import Blueprint
from models.payment import Payment
from models.user_payment import UserPayment
from utils.utils import get_response
from utils.decorators import role_required
from flask_restful import Api, Resource, reqparse

payment_create_parse = reqparse.RequestParser()
payment_create_parse.add_argument("user_payment_id", type=int, required=True, help="UserPayment ID cannot be blank")
payment_create_parse.add_argument("amount", type=float, required=True, help="Amount cannot be blank")
payment_create_parse.add_argument("type", type=str, required=True, help="Type cannot be blank")

payment_update_parse = reqparse.RequestParser()
payment_update_parse.add_argument("amount", type=float)
payment_update_parse.add_argument("type", type=str)

payment_bp = Blueprint("payment", __name__, url_prefix="/api/payment")
api = Api(payment_bp)

class PaymentResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self, payment_id):
        """Payment Get API
        Path - /api/payment/<payment_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: payment_id
              in: path
              type: integer
              required: true
              description: Enter Payment ID
        responses:
            200:
                description: Return a Payment
            404:
                description: Payment not found
        """
        payment = Payment.query.filter_by(id=payment_id).first()
        if not payment:
            return get_response("Payment not found", None, 404), 404

        return get_response("Payment successfully found", Payment.to_dict(payment), 200), 200

    def delete(self, payment_id):
        """Payment Delete API
        Path - /api/payment/<payment_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: payment_id
              in: path
              type: integer
              required: true
              description: Enter Payment ID
        responses:
            200:
                description: Delete a Payment
            404:
                description: Payment not found
        """
        payment = Payment.query.filter_by(id=payment_id).first()
        if not payment:
            return get_response("Payment not found", None, 404), 404

        db.session.delete(payment)
        db.session.commit()
        return get_response("Successfully deleted payment", None, 200), 200

    def patch(self, payment_id):
        """Payment Update API
        Path - /api/payment/<payment_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: payment_id
              in: path
              type: integer
              required: true
              description: Enter Payment ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    amount:
                        type: number
                    type:
                        type: string
        responses:
            200:
                description: Successfully updated payment
            404:
                description: Payment not found
        """
        found_payment = Payment.query.filter_by(id=payment_id).first()
        if not found_payment:
            return get_response("Payment not found", None, 404), 404

        data = payment_update_parse.parse_args()
        amount = data.get("amount", None)
        type_ = data.get("type", None)

        if amount is not None:
            found_payment.amount = amount
        if type_ is not None:
            found_payment.type = type_

        db.session.commit()
        return get_response("Successfully updated payment", None, 200), 200

class PaymentListCreateResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self):
        """Payment List API
        Path - /api/payment
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
                description: Return Payment List
        """
        payment_list = Payment.query.order_by(Payment.created_at.desc()).all()
        result = [Payment.to_dict(p) for p in payment_list]
        return get_response("Payment List", result, 200), 200

    def post(self):
        """Payment Create API
        Path - /api/payment
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
                    user_payment_id:
                        type: integer
                    amount:
                        type: number
                    type:
                        type: string
                required: [user_payment_id, amount, type]
        responses:
            200:
                description: Return New Payment ID
            400:
                description: user_payment_id, amount or type is blank
            404:
                description: UserPayment not found
        """
        data = payment_create_parse.parse_args()
        user_payment_id = data["user_payment_id"]
        amount = data["amount"]
        type_ = data["type"]

        found_user_payment = UserPayment.query.filter_by(id=user_payment_id).first()
        if not found_user_payment:
            return get_response("UserPayment not found", None, 404), 404

        new_payment = Payment(
            user_payment_id=user_payment_id,
            amount=amount,
            type=type_,
        )
        db.session.add(new_payment)
        db.session.commit()
        return get_response("Successfully created payment", new_payment.id, 200), 200

class PaymentByUserPaymentResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self, user_payment_id):
        """Payment List By UserPayment API
        Path - /api/payment/user_payment/<user_payment_id>
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
                description: Return Payment List for a UserPayment
            404:
                description: UserPayment not found
        """
        found_user_payment = UserPayment.query.filter_by(id=user_payment_id).first()
        if not found_user_payment:
            return get_response("UserPayment not found", None, 404), 404

        payment_list = Payment.query.filter_by(user_payment_id=user_payment_id).order_by(Payment.created_at.desc()).all()
        
        total_paid = sum(p.amount for p in payment_list)
        remaining = found_user_payment.course_price - (found_user_payment.discount or 0) - total_paid

        result = {
            "user_payment": UserPayment.to_dict(found_user_payment),
            "payments": [Payment.to_dict(p) for p in payment_list],
            "total_paid": total_paid,
            "remaining": remaining,
        }
        return get_response("Payment list successfully found", result, 200), 200

api.add_resource(PaymentResource, "/<payment_id>")
api.add_resource(PaymentListCreateResource, "/")
api.add_resource(PaymentByUserPaymentResource, "/user_payment/<user_payment_id>")
