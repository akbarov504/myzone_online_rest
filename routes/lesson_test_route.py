import random
from models import db
from datetime import date
from flask import Blueprint
from models.user import User
from models.lesson import Lesson
from utils.utils import get_response
from models.lesson_test import LessonTest
from utils.decorators import role_required
from models.lesson_student import LessonStudent
from flask_restful import Api, Resource, reqparse
from models.lesson_test_progress import LessonTestProgress

lesson_test_create_parse = reqparse.RequestParser()
lesson_test_create_parse.add_argument("lesson_id", type=int, required=True, help="Lesson ID cannot be blank")
lesson_test_create_parse.add_argument("question_text", type=str, required=True, help="Question Text cannot be blank")
lesson_test_create_parse.add_argument("option_a", type=str, required=True, help="Option A cannot be blank")
lesson_test_create_parse.add_argument("option_b", type=str, required=True, help="Option B cannot be blank")
lesson_test_create_parse.add_argument("option_c", type=str, required=True, help="Option C cannot be blank")
lesson_test_create_parse.add_argument("option_d", type=str, required=True, help="Option D cannot be blank")
lesson_test_create_parse.add_argument("correct_option", type=str, required=True, help="Correct Option cannot be blank")

lesson_test_update_parse = reqparse.RequestParser()
lesson_test_update_parse.add_argument("lesson_id", type=int)
lesson_test_update_parse.add_argument("question_text", type=str)
lesson_test_update_parse.add_argument("option_a", type=str)
lesson_test_update_parse.add_argument("option_b", type=str)
lesson_test_update_parse.add_argument("option_c", type=str)
lesson_test_update_parse.add_argument("option_d", type=str)
lesson_test_update_parse.add_argument("correct_option", type=str)

lesson_test_result_parse = reqparse.RequestParser()
lesson_test_result_parse.add_argument("answer_list", type=list, location="json", required=True, help="Answer List cannot be blank")

lesson_test_bp = Blueprint("lesson_test", __name__, url_prefix="/api/lesson_test")
api = Api(lesson_test_bp)

class LessonTestResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self, lesson_test_id):
        """Lesson Test Get API
        Path - /api/lesson_test/<lesson_test_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: lesson_test_id
              in: path
              type: integer
              required: true
              description: Enter Lesson Test ID
        responses:
            200:
                description: Return a Lesson Test
            404:
                description: Lesson Test not found
        """
        lesson_test = LessonTest.query.filter_by(id=lesson_test_id).first()
        if not lesson_test:
            return get_response("Lesson Test not found", None, 404), 404

        return get_response("Lesson Test successfully found", LessonTest.to_dict(lesson_test), 200), 200

    def delete(self, lesson_test_id):
        """Lesson Test Delete API
        Path - /api/lesson_test/<lesson_test_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: lesson_test_id
              in: path
              type: integer
              required: true
              description: Enter Lesson Test ID
        responses:
            200:
                description: Delete a Lesson Test
            404:
                description: Lesson Test not found
        """
        lesson_test = LessonTest.query.filter_by(id=lesson_test_id).first()
        if not lesson_test:
            return get_response("Lesson Test not found", None, 404), 404

        db.session.delete(lesson_test)
        db.session.commit()
        return get_response("Successfully deleted lesson test", None, 200), 200

    def patch(self, lesson_test_id):
        """Lesson Test Update API
        Path - /api/lesson_test/<lesson_test_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: lesson_test_id
              in: path
              type: integer
              required: true
              description: Enter Lesson Test ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    lesson_id:
                        type: integer
                    question_text:
                        type: string
                    option_a:
                        type: string
                    option_b:
                        type: string
                    option_c:
                        type: string
                    option_d:
                        type: string
                    correct_option:
                        type: string
        responses:
            200:
                description: Successfully updated lesson test
            404:
                description: Lesson Test not found
        """
        found_lesson_test = LessonTest.query.filter_by(id=lesson_test_id).first()
        if not found_lesson_test:
            return get_response("Lesson Test not found", None, 404), 404

        data = lesson_test_update_parse.parse_args()
        lesson_id = data.get('lesson_id', None)
        question_text = data.get('question_text', None)
        option_a = data.get('option_a', None)
        option_b = data.get('option_b', None)
        option_c = data.get('option_c', None)
        option_d = data.get('option_d', None)
        correct_option = data.get('correct_option', None)

        if lesson_id is not None:
            found_lesson_test.lesson_id = lesson_id
        if question_text is not None:
            found_lesson_test.question_text = question_text
        if option_a is not None:
            found_lesson_test.option_a = option_a
        if option_b is not None:
            found_lesson_test.option_b = option_b
        if option_c is not None:
            found_lesson_test.option_c = option_c
        if option_d is not None:
            found_lesson_test.option_d = option_d
        if correct_option is not None:
            correct_option = correct_option.upper()
            found_lesson_test.correct_option = correct_option

        db.session.commit()
        return get_response("Successfully updated lesson test", None, 200), 200

class LessonTestListCreateResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self, lesson_id):
        """Lesson Test List API
        Path - /api/lesson_test/lesson/<lesson_id>
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
                description: Return Lesson Test List
            404:
                description: Lesson not found
        """
        found_lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not found_lesson:
            return get_response("Lesson not found", None, 404), 404

        lesson_test_list = LessonTest.query.filter_by(lesson_id=found_lesson.id).order_by(LessonTest.created_at.desc()).all()
        result_lesson_test_list = [LessonTest.to_dict(lesson_test) for lesson_test in lesson_test_list]
        return get_response("Lesson Test List", result_lesson_test_list, 200), 200

    def post(self, lesson_id):
        """Lesson Test Create API
        Path - /api/lesson_test/lesson/<lesson_id>
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
                    lesson_id: 
                        type: integer
                    question_text:
                        type: string
                    option_a:
                        type: string
                    option_b:
                        type: string
                    option_c:
                        type: string
                    option_d:
                        type: string
                    correct_option:
                        type: string
                required: [lesson_id, question_text, option_a, option_b, option_c, option_d, correct_option]
        responses:
            200:
                description: Return New Lesson Test ID
            400:
                description: Lesson ID, Question Text, Option A, Option B, Option C, Option D or Correct Option is Blank
            404:
                description: Lesson not found
        """
        data = lesson_test_create_parse.parse_args()
        in_lesson_id = data['lesson_id']
        question_text = data['question_text']
        option_a = data['option_a']
        option_b = data['option_b']
        option_c = data['option_c']
        option_d = data['option_d']
        correct_option = data['correct_option']
        correct_option = correct_option.upper()

        found_lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not found_lesson:
            return get_response("Lesson not found", None, 404), 404
        
        new_lesson_test = LessonTest(in_lesson_id, question_text, option_a, option_b, option_c, option_d, correct_option)
        db.session.add(new_lesson_test)
        db.session.commit()
        return get_response("Successfully created lesson test", new_lesson_test.id, 200), 200

class LessonTestActionResource(Resource):
    decorators = [role_required(["ADMIN", "STUDENT"])]

    def get(self, lesson_id):
        """Lesson Test Action Get API
        Path - /api/lesson_test/action/<lesson_id>
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
                description: Return a Lesson Test
            404:
                description: Lesson not found
        """
        found_lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not found_lesson:
            return get_response("Lesson not found", None, 404), 404
        
        lesson_test_list = LessonTest.query.filter_by(lesson_id=found_lesson.id).all()
        lesson_test_random_list = random.sample(lesson_test_list, 10)

        result_lesson_test_random_list = [LessonTest.to_dict(lesson_test) for lesson_test in lesson_test_random_list]
        return get_response("Lesson Test successfully found", result_lesson_test_random_list, 200), 200
    
    def post(self, lesson_id):
        """Lesson Test Action POST API
        Path - /api/lesson_test/action/<lesson_id>
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
                    answer_list: 
                        type: list
                required: [answer_list]
        responses:
            200:
                description: Return Lesson Test Result
            400:
                description: (Answer List is Blank) or (Answer List must be a list)
            404:
                description: Lesson not found
        """
        data = lesson_test_result_parse.parse_args()
        answer_list = data['answer_list']

        found_lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not found_lesson:
            return get_response("Lesson not found", None, 404), 404
    
        if not answer_list or not isinstance(answer_list, list):
            return get_response("Answer List must be a list", None, 400), 400
    
        correct_count = 0
        for answer in answer_list:
            if not isinstance(answer, dict):
                continue
            
            lesson_test_id = answer.get('lesson_test_id')
            result = answer.get('result')

            if not lesson_test_id or not result:
                continue
            result = result.upper()

            lesson_test = LessonTest.query.filter_by(id=lesson_test_id, lesson_id=found_lesson.id).first()
            if lesson_test and lesson_test.correct_option == result:
                correct_count += 1
            
        passed = correct_count >= 7
        result_test = {
            "total": len(answer_list),
            "correct_count": correct_count,
            "passed": passed
        }
        
        return get_response("Lesson Test Result", result_test, 200), 200

class LessonTestFinishActionResource(Resource):
    decorators = [role_required(["ADMIN", "STUDENT"])]

    def get(self, student_id, lesson_id, correct_count):
        """Lesson Test Finish Action Get API
        Path - /api/lesson_test/finish/action/<student_id>/<lesson_id>/<correct_count>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: student_id
              in: path
              type: integer
              required: true
              description: Enter Student ID
            
            - name: lesson_id
              in: path
              type: integer
              required: true
              description: Enter Lesson ID
            
            - name: correct_count
              in: path
              type: integer
              required: true
              description: Enter Correct Count
        responses:
            200:
                description: Finish Lesson Test
            404:
                description: (Student not found) or (Lesson not found)
        """
        found_student = User.query.filter_by(id=student_id, role="STUDENT").first()
        if not found_student:
            return get_response("Student not found", None, 404), 404
        
        found_lesson = Lesson.query.filter_by(id=lesson_id).first()
        if not found_lesson:
            return get_response("Lesson not found", None, 404), 404
        
        progress = LessonTestProgress.query.filter_by(student_id=found_student.id, lesson_id=found_lesson.id).first()
        if not progress:
            progress = LessonTestProgress(found_student.id, found_lesson.id, False, 0)
        
        if progress.is_completed:
            return get_response("Successfully Finish Lesson Test", None, 200), 200

        correct_count = int(correct_count)
        progress.best_score = max(progress.best_score, correct_count)
        if correct_count >= 7:
            progress.is_completed = True
            next_lesson = Lesson.query.filter(Lesson.order == found_lesson.order + 1).first()

            if next_lesson:
                found_progress = LessonTestProgress.query.filter_by(student_id=found_student.id, lesson_id=next_lesson.id, is_completed=False).first()
                if not found_progress:
                    new_progress = LessonTestProgress(found_student.id, next_lesson.id, False, 0)
                    db.session.add(new_progress)
                    
                    today_date = date.today()
                    new_lesson_student = LessonStudent(found_student.id, today_date)
                    db.session.add(new_lesson_student)
        
        db.session.add(progress)
        db.session.commit()

        return get_response("Successfully Finish Lesson Test", None, 200), 200

api.add_resource(LessonTestResource, "/<lesson_test_id>")
api.add_resource(LessonTestListCreateResource, "/lesson/<lesson_id>")
api.add_resource(LessonTestActionResource, "/action/<lesson_id>")
api.add_resource(LessonTestFinishActionResource, "/finish/action/<student_id>/<lesson_id>/<correct_count>")
