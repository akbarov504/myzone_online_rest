from random import randint
from flask import Blueprint
from utils.utils import get_response
from flask_restful import Api, Resource
from utils.decorators import role_required

from models.user import User
from models.course import Course
from models.course_module import CourseModule
from models.module_test_progress import ModuleTestProgress

certificate_bp = Blueprint("certificate", __name__, url_prefix="/api/certificate")
api = Api(certificate_bp)

class CertificateResource(Resource):

    @role_required("STUDENT")
    def get(self, course_id, student_id):
        """Certificate Get API
        Path - /api/certificate/<course_id>/<student_id>
        Method - GET
        ---
        consumes: application/json
        parameters:
            - in: header
              name: Authorization
              type: string
              required: true
              description: Bearer token for authentication

            - name: course_id
              in: path
              type: integer
              required: true
              description: Enter Course ID

            - name: student_id
              in: path
              type: integer
              required: true
              description: Enter Student ID
        responses:
            200:
                description: Return a Certificate Details
            404:
                description: Course not found or Student not found or Module Test Progress not found
        """

        found_course = Course.query.filter_by(id=course_id).first()
        if not found_course:
            return get_response("Course not found", None, 404), 404
        
        found_student = User.query.filter_by(id=student_id, is_active=True).first()
        if not found_student or found_student.active_term <= 0:
            return get_response("Student not found", None, 404), 404
        
        best_score = 0
        completed_at = None
        reg_number = randint(1000, 9999)
        module_list = CourseModule.query.filter_by(course_id=found_course.id, is_active=True).all()
        for module in module_list:
            found_module_test_progress = ModuleTestProgress.query.filter_by(student_id=found_student.id, module_id=module.id, is_completed=True).first()
            if found_module_test_progress:
                best_score += found_module_test_progress.best_score
                completed_at = found_module_test_progress.created_at

        best_score = best_score * 1.25
        result = {
            "cource": Course.to_dict(found_course),
            "student": User.to_dict(found_student),
            "is_completed": True,
            "completed_at": str(completed_at),
            "reg_number": reg_number,
            "best_score": best_score
        }
        return get_response("Certificate Details", result, 200), 200

api.add_resource(CertificateResource, "/<course_id>/<student_id>")
