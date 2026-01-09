from models import db
from flask import Blueprint
from models.user import User
from utils.utils import get_response
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity
from models.support_ticket import SupportTicket
from models.support_message import SupportMessage
from flask_restful import Api, Resource, reqparse

support_ticket_create_parse = reqparse.RequestParser()
support_ticket_create_parse.add_argument("student_id", type=int, required=True, help="Student ID cannot be blank")
support_ticket_create_parse.add_argument("message", type=str, required=True, help="Message cannot be blank")
support_ticket_create_parse.add_argument("file_path", type=str)

support_ticket_bp = Blueprint("support_ticket", __name__, url_prefix="/api/support/ticket")
api = Api(support_ticket_bp)

class SupportTicketResource(Resource):

    @role_required(["SUPPORT", "STUDENT"])
    def get(self, ticket_id):
        """Support Ticket Get API
        Path - /api/support/ticket/<ticket_id>/messages
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: ticket_id
              in: path
              type: integer
              required: true
              description: Enter Ticket ID
        responses:
            200:
                description: Return a Messages
            404:
                description: Support Ticket not found
        """
        found_support_ticket = SupportTicket.query.filter_by(id=ticket_id).first()
        if not found_support_ticket:
            return get_response("Support Ticket not found", None, 404), 404
        
        support_message_list = SupportMessage.query.filter_by(ticket_id=found_support_ticket.id).order_by(SupportMessage.created_at.asc()).all()
        result_support_message_list = [SupportMessage.to_dict(support_message) for support_message in support_message_list]

        return get_response("Messages successfully found", result_support_message_list, 200), 200
    
    @role_required(["STUDENT"])
    def post(self, ticket_id):
        """Support Message Create API
        Path - /api/support/ticket/<ticket_id>/messages
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: ticket_id
              in: path
              type: integer
              required: true
              description: Enter Ticket ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    student_id: 
                        type: integer
                    message:
                        type: string
                    file_path:
                        type: string
                required: [student_id, message]
        responses:
            200:
                description: Return New Support Message ID
            400:
                description: Student ID or Message is Blank
            404:
                description: (Student not found) or (Ticket not found)
        """
        data = support_ticket_create_parse.parse_args()
        student_id = data['student_id']
        message = data['message']
        file_path = data['file_path']

        found_student = User.query.filter_by(id=student_id, role="STUDENT").first()
        if not found_student:
            return get_response("Student not found", None, 404), 404

        found_ticket = SupportTicket.query.filter_by(id=ticket_id, student_id=found_student.id).first()
        if not found_ticket or found_ticket.status == "CLOSED":
            return get_response("Ticket not found", None, 404), 404

        new_support_message = SupportMessage(found_ticket.id, found_student.id, found_student.role, message, file_path)
        db.session.add(new_support_message)
        db.session.commit()

        return get_response("Successfully created new support message", new_support_message.id, 200), 200

class SupportTicketListCreateResource(Resource):
    decorators = [role_required(["STUDENT"])]

    def get(self):
        """Support Ticket List API
        Path - /api/support/ticket
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
                description: Return Support Ticket List
            404:
                description: Student not found
        """
        username = get_jwt_identity()

        found_student = User.query.filter_by(username=username, role="STUDENT").first()
        if not found_student:
            return get_response("Student not found", None, 404), 404
        
        result_dict = {}
        result_unread_count = 0
        result_support_ticket_list = []

        support_ticket_list = SupportTicket.query.filter_by(student_id=found_student.id).order_by(SupportTicket.created_at.desc()).all()
        for support_ticket in support_ticket_list:
            unread_count = SupportMessage.query.filter(
                SupportMessage.ticket_id == support_ticket.id,
                SupportMessage.sender_role == "SUPPORT",
                SupportMessage.is_read == False
            ).count()
            result_unread_count += unread_count

            dict_support_ticket = SupportTicket.to_dict(support_ticket)
            result_support_ticket_list.append(dict_support_ticket)
        
        result_dict.update({"unread_count": result_unread_count})
        result_dict.update({"tickets": result_support_ticket_list})

        return get_response("Support Ticket List", result_dict, 200), 200

    def post(self):
        """Support Ticket Create API
        Path - /api/support/ticket
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
                    student_id: 
                        type: integer
                    message:
                        type: string
                    file_path:
                        type: string
                required: [student_id, message]
        responses:
            200:
                description: Return New Support Ticket ID
            400:
                description: Student ID or Message is Blank
            404:
                description: Student not found
        """
        data = support_ticket_create_parse.parse_args()
        student_id = data['student_id']
        message = data['message']
        file_path = data['file_path']

        found_student = User.query.filter_by(id=student_id, role="STUDENT").first()
        if not found_student:
            return get_response("Student not found", None, 404), 404
        
        new_support_ticket = SupportTicket(found_student.id, "OPEN")
        db.session.add(new_support_ticket)
        db.session.commit()

        new_support_message = SupportMessage(new_support_ticket.id, found_student.id, found_student.role, message, file_path)
        db.session.add(new_support_message)
        db.session.commit()

        return get_response("Successfully created new support ticket", new_support_ticket.id, 200), 200

class SupportTicketShowActionResource(Resource):
    decorators = [role_required(["SUPPORT"])]

    def get(self):
        """Support Ticket Show Action Get API
        Path - /api/support/ticket/inbox
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
                description: Return a Ticket List
        """
        result_dict = {}
        result_unread_count = 0
        result_support_ticket_list = []
        support_ticket_list = SupportTicket.query.order_by(SupportTicket.created_at.desc()).all()

        for support_ticket in support_ticket_list:
            found_student = User.query.filter_by(id=support_ticket.student_id, role="STUDENT").first()

            unread_count = SupportMessage.query.filter(
                SupportMessage.ticket_id == support_ticket.id,
                SupportMessage.sender_role == "STUDENT",
                SupportMessage.is_read == False
            ).count()
            result_unread_count += unread_count

            if found_student:
                dict_support_ticket = SupportTicket.to_dict(support_ticket)
                dict_found_student = User.to_dict(found_student)

                dict_support_ticket.update({"student": dict_found_student})
                result_support_ticket_list.append(dict_support_ticket)
            else:
                dict_support_ticket = SupportTicket.to_dict(support_ticket)

                dict_support_ticket.update({"student": None})
                result_support_ticket_list.append(dict_support_ticket)
        
        result_dict.update({"unread_count": result_unread_count})
        result_dict.update({"tickets": result_support_ticket_list})
        return get_response("Support Ticket List", result_dict, 200), 200

class SupportTicketReplyActionResource(Resource):
    decorators = [role_required(["SUPPORT"])]

    def post(self, ticket_id):
        """Support Ticket Reply Action POST API
        Path - /api/support/ticket/<ticket_id>/reply
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: ticket_id
              in: path
              type: integer
              required: true
              description: Enter Ticket ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    student_id: 
                        type: integer
                    message:
                        type: string
                    file_path:
                        type: string
                required: [student_id, message]
        responses:
            200:
                description: Return New Support Message ID
            400:
                description: Student ID or Message is Blank
            404:
                description: (User not found) or (Ticket not found)
        """
        username = get_jwt_identity()

        data = support_ticket_create_parse.parse_args()
        student_id = data['student_id']
        message = data['message']
        file_path = data['file_path']

        found_user = User.query.filter_by(username=username, role="SUPPORT").first()
        if not found_user:
            return get_response("User not found", None, 404), 404

        found_ticket = SupportTicket.query.filter_by(id=ticket_id, student_id=student_id).first()
        if not found_ticket or found_ticket.status == "CLOSED":
            return get_response("Ticket not found", None, 404), 404

        new_support_message = SupportMessage(found_ticket.id, found_user.id, found_user.role, message, file_path)
        db.session.add(new_support_message)
        db.session.commit()

        return get_response("Successfully created new support message", new_support_message.id, 200), 200

class SupportTicketCloseActionResource(Resource):
    decorators = [role_required(["SUPPORT"])]

    def post(self, ticket_id):
        """Support Ticket Close Action POST API
        Path - /api/support/ticket/<ticket_id>/close
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: ticket_id
              in: path
              type: integer
              required: true
              description: Enter Ticket ID
        responses:
            200:
                description: Support Ticket Close
            404:
                description: Ticket not found
        """
        found_ticket = SupportTicket.query.filter_by(id=ticket_id).first()
        if not found_ticket or found_ticket.status == "CLOSED":
            return get_response("Ticket not found", None, 404), 404

        found_ticket.status = "CLOSED"
        db.session.commit()

        return get_response("Successfully support ticket closed", None, 200), 200

api.add_resource(SupportTicketResource, "/<ticket_id>/messages")
api.add_resource(SupportTicketListCreateResource, "/")
api.add_resource(SupportTicketShowActionResource, "/inbox")
api.add_resource(SupportTicketReplyActionResource, "/<ticket_id>/reply")
api.add_resource(SupportTicketCloseActionResource, "/<ticket_id>/close")
