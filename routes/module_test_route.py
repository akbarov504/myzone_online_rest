import random
from models import db
from datetime import date
from flask import Blueprint
from models.user import User
from models.course import Course
from models.lesson import Lesson
from utils.utils import get_response
from models.module_test import ModuleTest
from utils.decorators import role_required
from models.course_module import CourseModule
from models.module_student import ModuleStudent
from flask_jwt_extended import get_jwt_identity
from flask_restful import Api, Resource, reqparse
from models.lesson_test_progress import LessonTestProgress
from models.module_test_progress import ModuleTestProgress

module_test_create_parse = reqparse.RequestParser()
module_test_create_parse.add_argument("module_id", type=int, required=True, help="Module ID cannot be blank")
module_test_create_parse.add_argument("question_text", type=str, required=True, help="Question Text cannot be blank")
module_test_create_parse.add_argument("option_a", type=str, required=True, help="Option A cannot be blank")
module_test_create_parse.add_argument("option_b", type=str, required=True, help="Option B cannot be blank")
module_test_create_parse.add_argument("option_c", type=str, required=True, help="Option C cannot be blank")
module_test_create_parse.add_argument("option_d", type=str, required=True, help="Option D cannot be blank")
module_test_create_parse.add_argument("correct_option", type=str, required=True, help="Correct Option cannot be blank")

module_test_update_parse = reqparse.RequestParser()
module_test_update_parse.add_argument("module_id", type=int)
module_test_update_parse.add_argument("question_text", type=str)
module_test_update_parse.add_argument("option_a", type=str)
module_test_update_parse.add_argument("option_b", type=str)
module_test_update_parse.add_argument("option_c", type=str)
module_test_update_parse.add_argument("option_d", type=str)
module_test_update_parse.add_argument("correct_option", type=str)

module_test_result_parse = reqparse.RequestParser()
module_test_result_parse.add_argument("answer_list", type=list, location="json", required=True, help="Answer List cannot be blank")

module_test_bp = Blueprint("module_test", __name__, url_prefix="/api/module_test")
api = Api(module_test_bp)

class ModuleTestResource(Resource):
    decorators = [role_required(["ADMIN"])]

    def get(self, module_test_id):
        """Module Test Get API
        Path - /api/module_test/<module_test_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: module_test_id
              in: path
              type: integer
              required: true
              description: Enter Module Test ID
        responses:
            200:
                description: Return a Module Test
            404:
                description: Module Test not found
        """
        module_test = ModuleTest.query.filter_by(id=module_test_id).first()
        if not module_test:
            return get_response("Module Test not found", None, 404), 404

        return get_response("Module Test successfully found", ModuleTest.to_dict(module_test), 200), 200

    def delete(self, module_test_id):
        """Module Test Delete API
        Path - /api/module_test/<module_test_id>
        Method - DELETE
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
              
            - name: module_test_id
              in: path
              type: integer
              required: true
              description: Enter Module Test ID
        responses:
            200:
                description: Delete a Module Test
            404:
                description: Module Test not found
        """
        module_test = ModuleTest.query.filter_by(id=module_test_id).first()
        if not module_test:
            return get_response("Module Test not found", None, 404), 404

        db.session.delete(module_test)
        db.session.commit()
        return get_response("Successfully deleted module test", None, 200), 200

    def patch(self, module_test_id):
        """Module Test Update API
        Path - /api/module_test/<module_test_id>
        Method - PATCH
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: module_test_id
              in: path
              type: integer
              required: true
              description: Enter Module Test ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    module_id:
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
                description: Successfully updated module test
            404:
                description: Module Test not found
        """
        found_module_test = ModuleTest.query.filter_by(id=module_test_id).first()
        if not found_module_test:
            return get_response("Module Test not found", None, 404), 404

        data = module_test_update_parse.parse_args()
        module_id = data.get('module_id', None)
        question_text = data.get('question_text', None)
        option_a = data.get('option_a', None)
        option_b = data.get('option_b', None)
        option_c = data.get('option_c', None)
        option_d = data.get('option_d', None)
        correct_option = data.get('correct_option', None)

        if module_id is not None:
            found_module_test.module_id = module_id
        if question_text is not None:
            found_module_test.question_text = question_text
        if option_a is not None:
            found_module_test.option_a = option_a
        if option_b is not None:
            found_module_test.option_b = option_b
        if option_c is not None:
            found_module_test.option_c = option_c
        if option_d is not None:
            found_module_test.option_d = option_d
        if correct_option is not None:
            correct_option = correct_option.upper()
            found_module_test.correct_option = correct_option

        db.session.commit()
        return get_response("Successfully updated module test", None, 200), 200

class ModuleTestListCreateResource(Resource):

    @role_required(["ADMIN", "STUDENT"])
    def get(self, module_id):
        """Module Test List API
        Path - /api/module_test/module/<module_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: module_id
              in: path
              type: integer
              required: true
              description: Enter Module ID

        responses:
            200:
                description: Return Module Test List
            404:
                description: Module not found
        """
        found_module = CourseModule.query.filter_by(id=module_id).first()
        if not found_module:
            return get_response("Module not found", None, 404), 404

        module_test_list = ModuleTest.query.filter_by(module_id=found_module.id).order_by(ModuleTest.created_at.desc()).all()
        result_module_test_list = [ModuleTest.to_dict(module_test) for module_test in module_test_list]
        return get_response("Module Test List", result_module_test_list, 200), 200

    @role_required(["ADMIN"])
    def post(self, module_id):
        """Module Test Create API
        Path - /api/module_test/module/<module_id>
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: module_id
              in: path
              type: integer
              required: true
              description: Enter Module ID

            - name: body
              in: body
              required: true
              schema:
                type: object
                properties:
                    module_id: 
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
                required: [module_id, question_text, option_a, option_b, option_c, option_d, correct_option]
        responses:
            200:
                description: Return New Module Test ID
            400:
                description: Module ID, Question Text, Option A, Option B, Option C, Option D or Correct Option is Blank
            404:
                description: Module not found
        """
        data = module_test_create_parse.parse_args()
        in_module_id = data['module_id']
        question_text = data['question_text']
        option_a = data['option_a']
        option_b = data['option_b']
        option_c = data['option_c']
        option_d = data['option_d']
        correct_option = data['correct_option']
        correct_option = correct_option.upper()

        found_module = CourseModule.query.filter_by(id=module_id).first()
        if not found_module:
            return get_response("Module not found", None, 404), 404
        
        new_module_test = ModuleTest(in_module_id, question_text, option_a, option_b, option_c, option_d, correct_option)
        db.session.add(new_module_test)
        db.session.commit()
        return get_response("Successfully created module test", new_module_test.id, 200), 200

class ModuleTestActionResource(Resource):
    decorators = [role_required(["ADMIN", "STUDENT"])]

    def get(self, module_id):
        """Module Test Action Get API
        Path - /api/module_test/action/<module_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: module_id
              in: path
              type: integer
              required: true
              description: Enter Module ID
        responses:
            200:
                description: Return a Module Test
            404:
                description: Module not found
        """
        found_module = CourseModule.query.filter_by(id=module_id).first()
        if not found_module:
            return get_response("Module not found", None, 404), 404
        
        module_test_list = ModuleTest.query.filter_by(module_id=found_module.id).all()
        module_test_random_list = random.sample(module_test_list, 40)

        result_module_test_random_list = [ModuleTest.to_dict(module_test) for module_test in module_test_random_list]
        return get_response("Module Test successfully found", result_module_test_random_list, 200), 200
    
    def post(self, module_id):
        """Module Test Action POST API
        Path - /api/module_test/action/<module_id>
        Method - POST
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication
            
            - name: module_id
              in: path
              type: integer
              required: true
              description: Enter Module ID

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
                description: Return Module Test Result
            400:
                description: (Answer List is Blank) or (Answer List must be a list)
            404:
                description: Module not found
        """
        data = module_test_result_parse.parse_args()
        answer_list = data['answer_list']

        found_module = CourseModule.query.filter_by(id=module_id).first()
        if not found_module:
            return get_response("Module not found", None, 404), 404
    
        if not answer_list or not isinstance(answer_list, list):
            return get_response("Answer List must be a list", None, 400), 400
    
        correct_count = 0
        for answer in answer_list:
            if not isinstance(answer, dict):
                continue
            
            module_test_id = answer.get('module_test_id')
            result = answer.get('result')

            if not module_test_id or not result:
                continue
            result = result.upper()

            module_test = ModuleTest.query.filter_by(id=module_test_id, module_id=found_module.id).first()
            if module_test and module_test.correct_option == result:
                correct_count += 1
            
        passed = correct_count >= 28
        result_test = {
            "total": len(answer_list),
            "correct_count": correct_count,
            "passed": passed
        }
        
        return get_response("Module Test Result", result_test, 200), 200

class ModuleTestFinishActionResource(Resource):
    decorators = [role_required(["ADMIN", "STUDENT"])]

    def get(self, student_id, module_id, correct_count):
        """Module Test Finish Action Get API
        Path - /api/module_test/finish/action/<student_id>/<module_id>/<correct_count>
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
            
            - name: module_id
              in: path
              type: integer
              required: true
              description: Enter Module ID
            
            - name: correct_count
              in: path
              type: integer
              required: true
              description: Enter Correct Count
        responses:
            200:
                description: Finish Module Test
            404:
                description: (Student not found) or (Module not found)
        """
        found_student = User.query.filter_by(id=student_id, role="STUDENT").first()
        if not found_student:
            return get_response("Student not found", None, 404), 404
        
        found_module = CourseModule.query.filter_by(id=module_id).first()
        if not found_module:
            return get_response("Module not found", None, 404), 404
        
        progress = ModuleTestProgress.query.filter_by(student_id=found_student.id, module_id=found_module.id).first()
        if not progress:
            progress = ModuleTestProgress(found_student.id, found_module.id, False, 0)
        
        correct_count = int(correct_count)
        progress.best_score = max(progress.best_score, correct_count)
        if correct_count >= 28:
            progress.is_completed = True
            next_module = CourseModule.query.filter(CourseModule.order == found_module.order + 1).first()

            if next_module:
                found_progress = ModuleTestProgress.query.filter_by(student_id=found_student.id, module_id=next_module.id, is_completed=False).first()
                if not found_progress:
                    new_progress = ModuleTestProgress(found_student.id, next_module.id, False, 0)
                    db.session.add(new_progress)
                    
                    today_date = date.today()
                    new_module_student = ModuleStudent(found_student.id, today_date)
                    db.session.add(new_module_student)
        
        db.session.add(progress)
        db.session.commit()

        return get_response("Successfully Finish Module Test", None, 200), 200

class ModuleTestListActionResource(Resource):
    decorators = [role_required(["STUDENT"])]

    def get(self):
        """Module Test List Action Get API
        Path - /api/module_test/list/action
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
                description: List Module
            404:
                description: (Student not found) or (Module not found)
        """
        username = get_jwt_identity()

        found_student = User.query.filter_by(username=username, role="STUDENT").first()
        if not found_student:
            return get_response("Student not found", None, 404), 404
        
        module_list = []
        today_date = date.today()
        module_student = ModuleStudent.query.filter_by(student_id=found_student.id, date=today_date).first()

        if module_student:
            course_list = Course.query.filter_by(type_id=found_student.type_id).all()
            for course in course_list:
                course_module_list = CourseModule.query.filter_by(course_id=course.id).all()
                for course_module in course_module_list:
                    module_test_list = ModuleTest.query.filter_by(module_id=course_module.id).all()
                    if len(module_test_list) <= 0:
                        continue
                    else:
                        lesson_list = Lesson.query.filter_by(course_module_id=course_module.id).order_by(Lesson.order.asc()).all()
                        lesson = lesson_list[-1]
                        lesson_test_progress = LessonTestProgress.query.filter_by(student_id=found_student.id, lesson_id=lesson.id, is_completed=True).first()
                        if lesson_test_progress is None:
                            result_dict = {
                                "is_open": False,
                                "is_passed": False
                            }

                            result_course_module = CourseModule.to_dict(course_module)
                            result_dict.update({"module": result_course_module})

                            module_list.append(result_dict)
                        else:
                            result_dict = {
                                "is_open": True
                            }

                            module_test_progress = ModuleTestProgress.query.filter_by(student_id=found_student.id, module_id=course_module.id, is_completed=True).first()
                            if module_test_progress is None:
                                result_dict.update({"is_passed": False})
                            else:
                                result_dict.update({"is_passed": True})

                            result_course_module = CourseModule.to_dict(course_module)
                            result_dict.update({"module": result_course_module})

                            module_list.append(result_dict)

            return get_response("Module List", module_list, 200)
        else:
            return get_response("Module List", module_list, 200)

api.add_resource(ModuleTestResource, "/<module_test_id>")
api.add_resource(ModuleTestListCreateResource, "/module/<module_id>")
api.add_resource(ModuleTestActionResource, "/action/<module_id>")
api.add_resource(ModuleTestFinishActionResource, "/finish/action/<student_id>/<module_id>/<correct_count>")
api.add_resource(ModuleTestListActionResource, "/list/action")
