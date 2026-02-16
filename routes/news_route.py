from models import db
from flask import Blueprint
from models.news import News
from utils.utils import get_response
from utils.decorators import role_required
from flask_restful import Api, Resource, reqparse

news_create_parse = reqparse.RequestParser()
news_create_parse.add_argument("title", type=str, required=True, help="Title cannot be blank")
news_create_parse.add_argument("description", type=str, required=True, help="Description cannot be blank")
news_create_parse.add_argument("content", type=str, required=True, help="Content cannot be blank")
news_create_parse.add_argument("file_url", type=str, required=True, help="File URL cannot be blank")
news_create_parse.add_argument("image_url", type=str, required=True, help="Image URL cannot be blank")

news_update_parse = reqparse.RequestParser()
news_update_parse.add_argument("title", type=str)
news_update_parse.add_argument("description", type=str)
news_update_parse.add_argument("content", type=str)
news_update_parse.add_argument("file_url", type=str)
news_update_parse.add_argument("image_url", type=str)

news_bp = Blueprint("news", __name__, url_prefix="/api/news")
api = Api(news_bp)

class NewsRecource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self):
        """News List API
        Path - /api/news
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
                description: Return a News List
        """
        news_list = News.query.all()
        result_news_list = [News.to_dict(news) for news in news_list]
        return get_response("News List", result_news_list, 200), 200
    
    @role_required(["ADMIN"])
    def post(self):
        """News Create API
        Path - /api/news
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
                    content:
                        type: string
                    file_url:
                        type: string
                    image_url:
                        type: string
                required: [title, description, content, file_url, image_url]
        responses:
            200:
                description: Return New News ID
            400:
                description: Title, Description, Content, File URL, Image URL is Blank
        """
        data = news_create_parse.parse_args()
        title = data['title']
        description = data['description']
        content = data['content']
        file_url = data['file_url']
        image_url = data['image_url']

        new_news = News(title, description, content, file_url, image_url)
        db.session.add(new_news)
        db.session.commit()
        return get_response("Successfully created news", new_news.id, 200), 200


class NewsDetailRecource(Resource):

    @role_required(["ADMIN"])
    def patch(self, news_id):
        """News Update API
        Path - /api/news/<news_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
    
            - name: news_id
              in: path
              type: integer
              required: true
              description: Enter News ID
            
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
                    content:
                        type: string
                    file_url:
                        type: string
                    image_url:
                        type: string
        responses:
            200:
                description: Successfully updated News
            404:
                description: News not found
        """
        found_news = News.query.filter_by(id=news_id).first()
        if not found_news:
            return get_response("News not found", None, 404), 404
        
        data = news_update_parse.parse_args()
        title = data.get('title', None)
        description = data.get('description', None)
        content = data.get('content', None)
        file_url = data.get('file_url', None)
        image_url = data.get('image_url', None)

        if title is not None:
            found_news.title = title
        if description is not None:
            found_news.description = description
        if content is not None:
            found_news.content = content
        if file_url is not None:
            found_news.file_url = file_url
        if image_url is not None:
            found_news.image_url = image_url

        db.session.commit()
        return get_response("Successfully updated news", None, 200), 200
    
    @role_required(["ADMIN"])
    def delete(self, news_id):
        """News Delete API
        Path - /api/news/<news_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: news_id
              in: path
              type: integer
              required: true
              description: Enter News ID
        responses:
            200:
                description: Delete a News
            404:
                description: News not found
        """
        found_news = News.query.filter_by(id=news_id).first()
        if not found_news:
            return get_response("News not found", None, 404), 404
        
        db.session.delete(found_news)
        db.session.commit()
        return get_response("Successfully deleted news", None, 200), 200
    
    @role_required(["ADMIN", "STUDENT"])
    def get(self, news_id):
        """News Get API
        Path - /api/news/<news_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: news_id
              in: path
              type: integer
              required: true
              description: Enter News ID
        responses:
            200:
                description: Return a News
            404:
                description: News not found
        """
        found_news = News.query.filter_by(id=news_id).first()
        if not found_news:
            return get_response("News not found", None, 404), 404
        
        return get_response("News successfully found", News.to_dict(found_news), 200), 200

api.add_resource(NewsRecource, "/")
api.add_resource(NewsDetailRecource, "/<news_id>")
