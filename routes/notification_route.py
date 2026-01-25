import pytz
from models import db
from flask import Blueprint
from models.user import User
from datetime import datetime
from utils.utils import get_response
from utils.decorators import role_required
from models.notification import Notification
from flask_restful import Api, Resource, reqparse
from models.notification_user import NotificationUser

time_zone = pytz.timezone("Asia/Tashkent")

notification_create_parse = reqparse.RequestParser()
notification_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
notification_create_parse.add_argument("message", type=str, required=True, help="Message cannot be blank")
notification_create_parse.add_argument("type", type=str, required=True, help="Type cannot be blank")
notification_create_parse.add_argument("is_global", type=bool, required=True, help="Is Global cannot be blank")

notification_update_parse = reqparse.RequestParser()
notification_update_parse.add_argument("title", type=str)
notification_update_parse.add_argument("message", type=str)
notification_update_parse.add_argument("type", type=str)

notification_read_parse = reqparse.RequestParser()
notification_read_parse.add_argument("notification_id", type=int, required=True, help="Notification ID cannot be blank")

notification_bp = Blueprint("notification", __name__, url_prefix="/api/notification")
api = Api(notification_bp)

class NotificationResource(Resource):

    @role_required(["ADMIN", "STUDENT", "TEACHER", "SUPPORT"])
    def get(self, notification_id):
        """Notification Get API
        Path - /api/notification/<notification_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: notification_id
              in: path
              type: integer
              required: true
              description: Enter Notification ID
        responses:
            200:
                description: Return a Notification
            404:
                description: Notification not found
        """
        notification = Notification.query.filter_by(id=notification_id).first()
        if not notification:
            return get_response("Notification not found", None, 404), 404

        return get_response("Notification successfully found", Notification.to_dict(notification), 200), 200

    @role_required(["ADMIN"])
    def delete(self, notification_id):
        """Notification Delete API
        Path - /api/notification/<notification_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: notification_id
              in: path
              type: integer
              required: true
              description: Enter Notification ID
        responses:
            200:
                description: Delete a Notification
            404:
                description: Notification not found
        """
        notification = Notification.query.filter_by(id=notification_id).first()
        if not notification:
            return get_response("Notification not found", None, 404), 404

        notification_user_list = NotificationUser.query.filter_by(notification_id=notification.id).all()
        for notification_user in notification_user_list:
            db.session.delete(notification_user)
            db.session.commit()

        db.session.delete(notification)
        db.session.commit()
        return get_response("Successfully deleted notification", None, 200), 200

    @role_required(["ADMIN"])
    def patch(self, notification_id):
        """Notification Update API
        Path - /api/notification/<notification_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: notification_id
              in: path
              type: integer
              required: true
              description: Enter Notification ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    title:
                        type: string
                    message:
                        type: string
                    type:
                        type: string
        responses:
            200:
                description: Successfully updated Notification
            404:
                description: Notification not found
        """
        found_notification = Notification.query.filter_by(id=notification_id).first()
        if not found_notification:
            return get_response("Notification not found", None, 404), 404

        data = notification_update_parse.parse_args()
        title = data.get('title', None)
        message = data.get('message', None)
        type = data.get('type', None)

        if title is not None:
            found_notification.title = title
        if message is not None:
            found_notification.message = message
        if type is not None:
            found_notification.type = type

        db.session.commit()
        return get_response("Successfully updated notification", None, 200), 200

class NotificationListCreateResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self):
        """Notification List API
        Path - /api/notification
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
                description: Return Notification List
        """
        notification_list = Notification.query.filter_by().order_by(Notification.created_at.desc()).all()
        result_notification_list = [Notification.to_dict(notification) for notification in notification_list]
        return get_response("Notification List", result_notification_list, 200), 200

    def post(self):
        """Notification Create API
        Path - /api/notification
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
                    message:
                        type: string
                    type:
                        type: string
                    is_global:
                        type: boolean
                required: [title, message, type, is_global]
        responses:
            200:
                description: Return New Notification ID
            400:
                description: Title, Message, Type, Is Global is Blank
        """
        data = notification_create_parse.parse_args()
        title = data['title']
        message = data['message']
        type = data['type']
        is_global = data['is_global']
        
        new_notification = Notification(title, message, type, is_global)
        db.session.add(new_notification)
        db.session.commit()
        return get_response("Successfully created notification", new_notification.id, 200), 200

class NotificationListReadResource(Resource):
    decorators = [role_required(["ADMIN", "STUDENT", "TEACHER", "SUPPORT"])]

    def get(self, user_id):
        """User Notification List API
        Path - /api/notification/user/<user_id>
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
                description: Return User Notification List
            404:
                description: User not found
        """

        found_user = User.query.filter_by(id=user_id, is_active=True).first()
        if not found_user:
            return get_response("User not found", None, 404), 404
        
        not_read_count = 0
        notification_list = []

        notification_user_list = NotificationUser.query.filter_by(user_id=found_user.id).all()
        for notification_user in notification_user_list:
            notification = Notification.query.filter_by(id=notification_user.notification_id).first()
            notification_list.append(notification)

            if not notification_user.is_read:
                not_read_count += 1

        result_notification_list = [Notification.to_dict(notification) for notification in notification_list]
        result_notification_user_list = [NotificationUser.to_dict(notification_user) for notification_user in notification_user_list]
        result = {
            "notification_count": len(notification_list),
            "not_read_count": not_read_count,
            "notifications": result_notification_list,
            "notification_users": result_notification_user_list
        }
        return get_response("User Notification List", result, 200), 200

    def post(self, user_id):
        """User Notification Read API
        Path - /api/notification/user/<user_id>
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
                    notification_id: 
                        type: integer
                required: [notification_id]

        responses:
            200:
                description: Successfully read a notification
            400:
                description: Notification ID is Blank
            404:
                description: User not found, Notification not found, Notification User not found
        """
        data = notification_read_parse.parse_args()
        notification_id = data['notification_id']

        found_user = User.query.filter_by(id=user_id, is_active=True).first()
        if not found_user:
            return get_response("User not found", None, 404), 404
        
        found_notification = Notification.query.filter_by(id=notification_id).first()
        if not found_notification:
            return get_response("Notification not found", None, 404), 404
        
        found_notification_user = NotificationUser.query.filter_by(notification_id=found_notification.id, user_id=found_user.id).first()
        if not found_notification_user:
            return get_response("Notification User not found", None, 404), 404
        
        found_notification_user.is_read = True
        found_notification_user.read_at = datetime.now(time_zone)
        db.session.commit()
        return get_response("Successfully read a notification", None, 200), 200

api.add_resource(NotificationResource, "/<notification_id>")
api.add_resource(NotificationListReadResource, "/user/<user_id>")
api.add_resource(NotificationListCreateResource, "/")
