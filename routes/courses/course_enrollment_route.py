from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from database import db
from models import Course, StudentCourse

api = Namespace('course_enrollment', description='Course Enrollment operations')

from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from database import db
from models import Course, StudentCourse

api = Namespace('course_enrollment', description='Course Enrollment operations')

@api.route('/<int:course_id>')
class CourseEnrollment(Resource):
    @jwt_required()
    def post(self, course_id):
        """
        Tilmeld en studerende til et kursus.
        """
        try:
            student_identity = get_jwt_identity()
            student_id = student_identity["id"] if isinstance(student_identity, dict) else student_identity
            print(f"Student ID: {student_id}, Course ID: {course_id}")

            course = db.session.query(Course).filter_by(course_id=course_id).first()
            if not course:
                print("Course not found")
                return {"error": "Course not found"}, 404

            existing_enrollment = db.session.query(StudentCourse).filter_by(
                student_id=student_id, course_id=course_id
            ).first()
            if existing_enrollment:
                print("Already enrolled")
                return {"message": "Already enrolled"}, 200

            new_enrollment = StudentCourse(student_id=student_id, course_id=course_id)
            db.session.add(new_enrollment)
            db.session.commit()

            return {"message": "Enrollment successful"}, 201

        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            db.session.rollback()
            return {"error": "An error occurred while enrolling in the course"}, 500

    @jwt_required()
    def delete(self, course_id):
        """
        Afmeld en studerende fra et kursus.
        """
        try:
            student_identity = get_jwt_identity()
            student_id = student_identity["id"] if isinstance(student_identity, dict) else student_identity
            print(f"Student ID: {student_id}, Course ID: {course_id}")

            enrollment = db.session.query(StudentCourse).filter_by(student_id=student_id, course_id=course_id).first()
            if not enrollment:
                print("Enrollment not found")  
                return {
                    "error": "Enrollment not found. You are not enrolled in this course."
                }, 404

            db.session.delete(enrollment)
            db.session.commit()

            print("Unenrollment successful")
            return {"message": "Unenrollment successful"}, 200

        except SQLAlchemyError as e:
            print(f"Database error: {e}") 
            db.session.rollback()
            return {"error": "An error occurred while unenrolling"}, 500



    @jwt_required()
    def get(self, course_id):
        """
        Tjek status for, om en studerende er tilmeldt et kursus.
        """
        try:
            student_identity = get_jwt_identity()
            student_id = student_identity["id"] if isinstance(student_identity, dict) else student_identity
            print(f"Student ID: {student_id}, Course ID: {course_id}")  

            enrollment = db.session.query(StudentCourse).filter_by(student_id=student_id, course_id=course_id).first()
            if not enrollment:
                return {"status": "Not enrolled"}, 200

            return {
                "status": "Enrolled",
                "enrolled_at": enrollment.enrolled_at.strftime('%Y-%m-%d %H:%M:%S') if enrollment.enrolled_at else None
            }, 200

        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return {"error": "An error occurred while checking enrollment status"}, 500

