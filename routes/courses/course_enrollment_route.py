from flask import app, current_app
from flask_restx import Namespace, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import jsonify
from sqlalchemy.exc import SQLAlchemyError
from database import db
from models import Course, StudentCourse

api = Namespace('course_enrollment', description='Course Enrollment operations')

def get_user_id():
    student_identity = get_jwt_identity()
    return student_identity["id"] if isinstance(student_identity, dict) else student_identity

def get_course(course_id):
    return db.session.query(Course).filter_by(course_id=course_id).first()

def get_enrollment(student_id, course_id):
    return db.session.query(StudentCourse).filter_by(student_id=student_id, course_id=course_id).first()

@api.route('/<int:course_id>')
class CourseEnrollment(Resource):
    @jwt_required()
    def post(self, course_id):
        """
        Tilmeld en studerende til et kursus.
        """
        try:
            student_id = get_user_id()
            course = get_course(course_id)

            if not course:
                return {"error": "Course not found"}, 404

            if get_enrollment(student_id, course_id):
                return {"message": "Already enrolled"}, 200

            new_enrollment = StudentCourse(student_id=student_id, course_id=course_id)
            db.session.add(new_enrollment)
            db.session.commit()

            return {"message": "Enrollment successful"}, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "An error occurred while enrolling in the course"}, 500

    @jwt_required()
    def delete(self, course_id):
        """
        Afmeld en studerende fra et kursus.
        """
        try:
            student_id = get_user_id()
            enrollment = get_enrollment(student_id, course_id)

            if not enrollment:
                return {"error": "Enrollment not found. You are not enrolled in this course."}, 404

            db.session.delete(enrollment)
            db.session.commit()

            return {"message": "Unenrollment successful"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            return {"error": "An error occurred while unenrolling"}, 500

    @jwt_required()
    def get(self, course_id):
        """
        Tjek status for, om en studerende er tilmeldt et kursus.
        """
        try:
            student_id = get_user_id()
            enrollment = get_enrollment(student_id, course_id)

            if not enrollment:
                return {"status": "Not enrolled"}, 200

            return {
                "status": "Enrolled",
                "enrolled_at": enrollment.enrolled_at.strftime('%Y-%m-%d %H:%M:%S') if enrollment.enrolled_at else None
            }, 200

        except SQLAlchemyError as e:
            return {"error": "An error occurred while checking enrollment status"}, 500

    
@api.route('/<int:course_id>/complete')
class CourseCompletion(Resource):
    @jwt_required()
    def post(self, course_id):
        """
        Marker et kursus som gennemført for en studerende.
        """
        user_id = get_user_id()
        try:
            enrollment = db.session.query(StudentCourse).filter_by(
                course_id=course_id, student_id=user_id
            ).first()

            if not enrollment:
                return {"error": "Enrollment not found"}, 404

            enrollment.completed = True
            db.session.commit()

            return {"message": "Kursus gennemført"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error completing course: {str(e)}")
            return {"error": "An error occurred while completing the course"}, 500


@api.route('/<int:course_id>/complete')
class CourseCompletionStatus(Resource):
    @jwt_required()
    def get(self, course_id):
        """
        Tjek, om et kursus er gennemført af en studerende.
        """
        user_id = get_user_id()
        try:
            enrollment = db.session.query(StudentCourse).filter_by(
                course_id=course_id, student_id=user_id
            ).first()

            if not enrollment:
                print(f"No enrollment found for course_id={course_id}, user_id={user_id}")
                return {"completed": False, "message": "Not enrolled in the course"}, 404

            completed = getattr(enrollment, "completed", False)
            return {"completed": completed}, 200

        except SQLAlchemyError as e:
            print(f"Database error while checking course completion status: {e}")
            return {"error": "An error occurred while checking course completion status"}, 500



