from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restx import Namespace, Resource, fields
from flask import request
from models import Course, UserXP
from database import db

api = Namespace('xp', description='Operations related to XP management')

def get_user_id():
    student_identity = get_jwt_identity()
    return student_identity["id"] if isinstance(student_identity, dict) else student_identity

xp_model = api.model('XPModel', {
    'course_id': fields.Integer(required=True, description='The ID of the course'),
    'xp_earned': fields.Integer(required=True, description='The amount of XP earned')
})

example_input = {
    "course_id": 101,
    "xp_earned": 50
}

@api.route('')
class AddXP(Resource):
    @jwt_required()
    @api.expect(xp_model, validate=True)
    @api.response(201, 'XP successfully added.')
    @api.response(400, 'Invalid input. course_id and xp_earned are required.')
    @api.response(404, 'Course not found.')
    @api.response(500, 'Internal server error.')
    def post(self):
        try:
            user_id = get_user_id()
            print("User ID from token:", user_id)

            data = request.get_json()
            course_id = data.get('course_id')
            xp_earned = data.get('xp_earned')

            if not all([course_id, xp_earned]):
                print("Missing fields: course_id or xp_earned")
                return {'error': 'Missing required fields'}, 400

            existing_xp = db.session.query(UserXP).filter_by(user_id=user_id, course_id=course_id).first()
            if existing_xp:
                print(f"XP already exists for user_id={user_id}, course_id={course_id}")
                return {'error': 'XP already added for this course and user'}, 400

            new_xp = UserXP(user_id=user_id, course_id=course_id, xp_earned=xp_earned)
            db.session.add(new_xp)
            db.session.commit()

            print(f"XP successfully added for user_id={user_id}, course_id={course_id}, xp_earned={xp_earned}")
            return {'message': 'XP successfully added'}, 201

        except Exception as e:
            print("Error adding XP:", str(e))
            db.session.rollback()
            return {'error': 'Internal server error', 'details': str(e)}, 500
        
@api.route('/<int:user_id>/total')
class GetUserTotalXP(Resource):
    @jwt_required()
    @api.response(200, 'Total XP retrieved successfully.')
    @api.response(404, 'User not found.')
    @api.response(500, 'Internal server error.')
    @api.doc(
        description="Retrieve the total XP for a specific user by user_id.",
        params={
            'user_id': 'The ID of the user for whom to retrieve the total XP.',
            'Authorization': 'Bearer <access_token>'
        },
        responses={
            200: 'Total XP retrieved successfully.',
            404: 'User not found.',
            500: 'Internal server error.'
        },
        example={"user_id": 123, "total_xp": 150}
    )
    def get(self, user_id):
        """Get the total XP for a specific user by user_id"""
        try:
            total_xp = db.session.query(db.func.sum(UserXP.xp_earned)).filter_by(user_id=user_id).scalar()
            total_xp = total_xp if total_xp else 0

            print(f"Total XP for user_id={user_id}: {total_xp}")
            return {'user_id': user_id, 'total_xp': total_xp}, 200

        except Exception as e:
            print("Error retrieving total XP for user:", str(e))
            return {'error': 'Internal server error', 'details': str(e)}, 500


@api.route('/total')
class GetCurrentUserTotalXP(Resource):
    @jwt_required()
    @api.response(200, 'Total XP retrieved successfully.')
    @api.response(500, 'Internal server error.')
    @api.doc(
        description="Retrieve the total XP for the current authenticated user.",
        params={'Authorization': 'Bearer <access_token>'},
        responses={
            200: 'Total XP retrieved successfully.',
            500: 'Internal server error.'
        },
        example={"user_id": 123, "total_xp": 150}
    )
    def get(self):
        """Get the total XP for the current user"""
        try:
            user_id = get_user_id()
            print("User ID from token:", user_id)

            total_xp = db.session.query(db.func.sum(UserXP.xp_earned)).filter_by(user_id=user_id).scalar()
            total_xp = total_xp if total_xp else 0

            print(f"Total XP for current user_id={user_id}: {total_xp}")
            return {'user_id': user_id, 'total_xp': total_xp}, 200

        except Exception as e:
            print("Error retrieving total XP for current user:", str(e))
            return {'error': 'Internal server error', 'details': str(e)}, 500


