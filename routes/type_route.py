from models import db
from flask import Blueprint
from models.type import Type
from utils.utils import get_response
from utils.decorators import role_required
from flask_restful import Api, Resource, reqparse

type_create_parse = reqparse.RequestParser()
type_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
type_create_parse.add_argument("description", type=str, required=True, help="Description cannot be blank")

type_update_parse = reqparse.RequestParser()
type_update_parse.add_argument("title", type=str)
type_update_parse.add_argument("description", type=str)

type_bp = Blueprint("type", __name__, url_prefix="/api/type")
api = Api(type_bp)

class TypeResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self, type_id):
        """Type Get API
        Path - /api/type/<type_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: type_id
              in: path
              type: integer
              required: true
              description: Enter Type ID
        responses:
            200:
                description: Return a Type
            404:
                description: Type not found
        """
        type = Type.query.filter_by(id=type_id).first()
        if not type:
            return get_response("Type not found", None, 404), 404

        return get_response("Type successfully found", Type.to_dict(type), 200), 200

    def delete(self, type_id):
        """Type Delete API
        Path - /api/type/<type_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: type_id
              in: path
              type: integer
              required: true
              description: Enter Type ID
        responses:
            200:
                description: Delete a Type
            404:
                description: Type not found
        """
        type = Type.query.filter_by(id=type_id).first()
        if not type:
            return get_response("Type not found", None, 404), 404

        db.session.delete(type)
        db.session.commit()
        return get_response("Successfully deleted type", None, 200), 200

    def patch(self, type_id):
        """Type Update API
        Path - /api/type/<type_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: type_id
              in: path
              type: integer
              required: true
              description: Enter Type ID

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
        responses:
            200:
                description: Successfully updated type
            404:
                description: Type not found
        """
        found_type = Type.query.filter_by(id=type_id).first()
        if not found_type:
            return get_response("Type not found", None, 404), 404

        data = type_update_parse.parse_args()
        title = data.get('title', None)
        description = data.get('description', None)

        if title is not None:
            found_type.title = title
        if description is not None:
            found_type.description = description

        db.session.commit()
        return get_response("Successfully updated type", None, 200), 200

class TypeListCreateResource(Resource):
    
    @role_required(["ADMIN", "STUDENT"])
    def get(self):
        """Type List API
        Path - /api/type
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
                description: Return Type List
        """
        type_list = Type.query.filter_by().order_by(Type.created_at.desc()).all()
        result_type_list = [Type.to_dict(type) for type in type_list]
        return get_response("Type List", result_type_list, 200), 200

    @role_required(["ADMIN"])
    def post(self):
        """Type Create API
        Path - /api/type
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
                    description:
                        type: string
                required: [title, description]
        responses:
            200:
                description: Return New Type ID
            400:
                description: (Title, Description is Blank) or (Type with this Title already exists)
        """
        data = type_create_parse.parse_args()
        title = data['title']
        description = data['description']

        type = Type.query.filter_by(title=title).first()
        if type:
            return get_response("Type Title already exists", None, 400), 400
        
        new_type = Type(title, description)
        db.session.add(new_type)
        db.session.commit()
        return get_response("Successfully created type", new_type.id, 200), 200

api.add_resource(TypeResource, "/<type_id>")
api.add_resource(TypeListCreateResource, "/")
