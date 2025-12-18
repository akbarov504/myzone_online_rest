from models import db
from flask import Blueprint
from models.lesson import Lesson
from utils.utils import get_response
from utils.decorators import role_required
from models.lesson_material import LessonMaterial
from flask_restful import Api, Resource, reqparse

lesson_material_create_parse = reqparse.RequestParser()
lesson_material_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
lesson_material_create_parse.add_argument("description", type=str, required=True, help="Description cannot be blank")
lesson_material_create_parse.add_argument("material_url", type=str, required=True, help="Material URL cannot be blank")

lesson_material_update_parse = reqparse.RequestParser()
lesson_material_update_parse.add_argument("lesson_id", type=int)
lesson_material_update_parse.add_argument("title", type=str)
lesson_material_update_parse.add_argument("description", type=str)
lesson_material_update_parse.add_argument("material_url", type=str)

lesson_material_bp = Blueprint("lesson_material", __name__, url_prefix="/api/lesson_material")
api = Api(lesson_material_bp)

class LessonMaterialResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, lesson_material_id):
        """Lesson Material Get API
        Path - /api/lesson_material/<lesson_material_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: lesson_material_id
              in: path
              type: integer
              required: true
              description: Enter Lesson Material ID
        responses:
            200:
                description: Return a Lesson Material
            404:
                description: Lesson Material not found
        """
        lesson_material = LessonMaterial.query.filter_by(id=lesson_material_id).first()
        if not lesson_material:
            return get_response("Lesson Material not found", None, 404), 404

        return get_response("Lesson Material successfully found", LessonMaterial.to_dict(lesson_material), 200), 200

    @role_required(["ADMIN"])
    def delete(self, lesson_material_id):
        """Lesson Material Delete API
        Path - /api/lesson_material/<lesson_material_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: lesson_material_id
              in: path
              type: integer
              required: true
              description: Enter Lesson Material ID
        responses:
            200:
                description: Delete a Lesson Material
            404:
                description: Lesson Material not found
        """
        lesson_material = LessonMaterial.query.filter_by(id=lesson_material_id).first()
        if not lesson_material:
            return get_response("Lesson Material not found", None, 404), 404

        db.session.delete(lesson_material)
        db.session.commit()
        return get_response("Successfully deleted lesson material", None, 200), 200

    @role_required(["ADMIN"])
    def patch(self, lesson_material_id):
        """Lesson Material Update API
        Path - /api/lesson_material/<lesson_material_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: lesson_material_id
              in: path
              type: integer
              required: true
              description: Enter Lesson Material ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    lesson_id:
                        type: integer
                    title:
                        type: string
                    description:
                        type: string
                    material_url:
                        type: string
        responses:
            200:
                description: Successfully updated lesson material
            404:
                description: Lesson Material not found
        """
        found_lesson_material = LessonMaterial.query.filter_by(id=lesson_material_id).first()
        if not found_lesson_material:
            return get_response("Lesson Material not found", None, 404), 404

        data = lesson_material_update_parse.parse_args()
        lesson_id = data.get('lesson_id', None)
        title = data.get('title', None)
        description = data.get('description', None)
        material_url = data.get('material_url', None)

        if lesson_id is not None:
            found_lesson_material.lesson_id = lesson_id
        if title is not None:
            found_lesson_material.title = title
        if description is not None:
            found_lesson_material.description = description
        if material_url is not None:
            found_lesson_material.material_url = material_url

        db.session.commit()
        return get_response("Successfully updated lesson material", None, 200), 200

class LessonMaterialListCreateResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, lesson_id):
        """Lesson Material List API
        Path - /api/lesson_material/lesson/<lesson_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: lesson_id
              in: path
              type: integer
              required: true
              description: Enter Lesson ID

        responses:
            200:
                description: Return Lesson Material List
            404:
                description: Lesson not found
        """
        found_lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not found_lesson:
            return get_response("Lesson not found", None, 404), 404

        lesson_material_list = LessonMaterial.query.filter_by(lesson_id=found_lesson.id).order_by(LessonMaterial.created_at.desc()).all()
        result_lesson_material_list = [LessonMaterial.to_dict(lesson_material) for lesson_material in lesson_material_list]
        return get_response("Lesson Material List", result_lesson_material_list, 200), 200

    @role_required(["ADMIN"])
    def post(self, lesson_id):
        """Lesson Material Create API
        Path - /api/lesson_material/lesson/<lesson_id>
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: lesson_id
              in: path
              type: integer
              required: true
              description: Enter Lesson ID

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
                    material_url:
                        type: string
                required: [title, description, material_url]
        responses:
            200:
                description: Return New Lesson Material ID
            400:
                description: (Title, Description, Material URL is Blank) or (Lesson Material with this Title already exists)
            404:
                description: Lesson not found
        """
        data = lesson_material_create_parse.parse_args()
        title = data['title']
        description = data['description']
        material_url = data['material_url']

        found_lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not found_lesson:
            return get_response("Lesson not found", None, 404), 404

        lesson_material = LessonMaterial.query.filter_by(title=title, lesson_id=found_lesson.id).first()
        if lesson_material:
            return get_response("Lesson Material Title already exists", None, 400), 400
        
        new_lesson_material = LessonMaterial(found_lesson.id, title, description, material_url)
        db.session.add(new_lesson_material)
        db.session.commit()
        return get_response("Successfully created lesson material", new_lesson_material.id, 200), 200

api.add_resource(LessonMaterialResource, "/<lesson_material_id>")
api.add_resource(LessonMaterialListCreateResource, "/lesson/<lesson_id>")
