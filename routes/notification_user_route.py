from models import db
from flask import Blueprint
from models.user import User
from utils.utils import get_response
from utils.decorators import role_required
from models.notification import Notification
from flask_restful import Api, Resource, reqparse
from models.notification_user import NotificationUser

notification_user_parse = reqparse.RequestParser()
notification_user_parse.add_argument("user_id", type=int, required=True, help="User ID cannot be blank")
notification_user_parse.add_argument("notification_id", type=int, required=True, help="Notification ID cannot be blank")

notification_user_bp = Blueprint("notification_user", __name__, url_prefix="/api/notification_user")
api = Api(notification_user_bp)

class NotificationUserResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def post(self):
        """Notification User Create API
        Path - /api/notification_user
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
                    notification_id:
                        type: integer
                required: [user_id, notification_id]
        responses:
            200:
                description: Return New Notification User ID
            400:
                description: User ID or Notification ID is Blank
            404:
                description: User not found, Notification not found
        """
        data = notification_user_parse.parse_args()
        user_id = data['user_id']
        notification_id = data['notification_id']

        found_user = User.query.filter_by(id=user_id, is_active=True).first()
        if not found_user:
            return get_response("User not found", None, 404), 404
        
        found_notification = Notification.query.filter_by(id=notification_id).first()
        if not found_notification:
            return get_response("Notification not found", None, 404), 404
        
        found_notification_user = NotificationUser.query.filter_by(user_id=found_user.id, notification_id=found_notification.id).first()
        if found_notification_user:
            return get_response("Successfully created notification user", found_notification_user.id, 200), 200
        
        new_notification_user = NotificationUser(found_notification.id, found_user.id)
        db.session.add(new_notification_user)
        db.session.commit()
        return get_response("Successfully created notification user", new_notification_user.id, 200), 200

api.add_resource(NotificationUserResource, "/")
