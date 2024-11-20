from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError
from models import Account
from database import db

from flasgger import Swagger, swag_from

user_bp = Blueprint('user_bp', __name__)

class UserRoutes():

    @user_bp.route("/login", methods=["POST"])
    @swag_from({
        'summary': 'User Login',
        'description': 'Login with username and password.',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'username': {
                            'type': 'string',
                            'example': 'admin'
                        },
                        'password': {
                            'type': 'string',
                            'example': 'admin'
                        }
                    }
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Successful login',
                'examples': {
                    'application/json': {"success": True}
                }
            },
            400: {
                'description': 'Missing username or password',
                'examples': {
                    'application/json': {"error": "Failed to login"}
                }
            },
            401: {
                'description': 'Invalid credentials',
                'examples': {
                    'application/json': {"error": "Invalid credentials"}
                }
            }
        }
    })
    def user_login():
        data = request.get_json()
        if "username" not in data or "password" not in data:
            return jsonify({"error": "Failed to login"}), 400
        if data["username"] == "admin" and data["password"] == "admin":
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401


    @user_bp.route('/register', methods=['POST'])
    @swag_from({
        'tags': ['User Registration'],
        'summary': 'Register a new user',
        'description': 'Allows a new user to register by providing their full name, email, and password.',
        'parameters': [
            {
                'name': 'body',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'fullName': {
                            'type': 'string',
                            'example': 'John Doe'
                        },
                        'email': {
                            'type': 'string',
                            'example': 'johndoe@example.com'
                        },
                        'password': {
                            'type': 'string',
                            'example': 'SecurePassword123'
                        }
                    }
                }
            }
        ],
        'responses': {
            201: {
                'description': 'User registered successfully',
                'examples': {
                    'application/json': {'message': 'User created successfully'}
                }
            },
            400: {
                'description': 'Invalid input or email already exists',
                'examples': {
                    'application/json': {'error': 'Invalid request form'}
                }
            }
        }
    })
    def register_user(): 
        register_form = request.json
        full_name = register_form.get('fullName')
        email = register_form.get('email')
        password = register_form.get('password')

        if not full_name or not email or not password:
            return jsonify({"error": "Invalid request form"}), 400 
            
        salt = '33b0b69bbe83498dbe7c403ff309d44d'
        hashed_password = generate_password_hash(str(password).lower() + salt)


        try:
            new_account = Account(
                name=full_name,
                email=email,
                password=hashed_password,
                role_id=1  
            )
            db.session.add(new_account)
            db.session.commit()
            return jsonify({"message": "User created successfully"}), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Email already exists"}), 400
