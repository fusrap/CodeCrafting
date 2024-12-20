from flask import Blueprint, jsonify, request
from argon2 import PasswordHasher, exceptions
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from models import Account
from database import db

from flasgger import Swagger, swag_from

user_bp = Blueprint('user_bp', __name__)
ph = PasswordHasher()

class UserRoutes():

    @user_bp.route("/login_test", methods=["POST"])
    @swag_from({
        'summary': 'User Login (test)',
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

        try:
            hashed_password = ph.hash(password)

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
        

@user_bp.route('/login', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'User Login',
    'description': 'Authenticate a user by verifying their email and password. Returns a JWT access token if the credentials are valid.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'email': {
                        'type': 'string',
                        'example': 'testuser@example.com',
                        'description': 'The email address of the user'
                    },
                    'password': {
                        'type': 'string',
                        'example': '123',
                        'description': 'The password of the user'
                    }
                },
                'required': ['email', 'password']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Successful login. Returns a JWT token.',
            'schema': {
                'type': 'object',
                'properties': {
                    'message': {
                        'type': 'string',
                        'example': 'Login successful'
                    },
                    'access_token': {
                        'type': 'string',
                        'example': 'eyJ0eXAiOiJKV1QiLCJh...'
                    }
                }
            }
        },
        400: {
            'description': 'Invalid request due to missing fields.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Email and password are required'
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized due to invalid credentials.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Invalid email or password'
                    }
                }
            }
        },
        500: {
            'description': 'Internal server error during login.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'An error occurred during login'
                    },
                    'details': {
                        'type': 'string',
                        'example': 'Detailed error message'
                    }
                }
            }
        }
    }
})
def authenticate_user():
    login_details = request.json
    email = login_details.get('email')
    password = login_details.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        with db.engine.connect() as connection:
            session = Session(connection)
            user = session.query(Account).filter_by(email=email).first()

        if user is None:
            return jsonify({"error": "Invalid email or password"}), 401

        try:
            ph.verify(user.password, password) 
        except exceptions.VerifyMismatchError:
            return jsonify({"error": "Invalid email or password"}), 401

        # Opret access og refresh tokens
        access_token = create_access_token(identity={"id": user.account_id, "email": user.email, "name": user.name, "role_id": user.role_id})
        refresh_token = create_refresh_token(identity={"id": user.account_id, "email": user.email, "role_id": user.role_id})

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "refresh_token": refresh_token
        }), 200

    except Exception as e:
        return jsonify({"error": "An error occurred during login", "details": str(e)}), 500

    

@user_bp.route('/refresh-token', methods=['POST'])
@swag_from({
    'tags': ['Authentication'],
    'summary': 'Refresh JWT Token',
    'description': 'Generate a new JWT token using the existing valid token.',
    'responses': {
        200: {
            'description': 'New token generated successfully.',
            'schema': {
                'type': 'object',
                'properties': {
                    'access_token': {
                        'type': 'string',
                        'example': 'eyJ0eXAiOiJKV1QiLCJh...'
                    }
                }
            }
        },
        401: {
            'description': 'Unauthorized due to invalid or expired token.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {
                        'type': 'string',
                        'example': 'Token is invalid or expired'
                    }
                }
            }
        }
    }
})
@user_bp.route('/refresh-token', methods=['POST'], endpoint="user_refresh_token")
@jwt_required(refresh=True)  # Kræver, at anmodningen bruger et refresh token
def refresh_token():
    try:
        # Henter identity fra refresh token
        current_user = get_jwt_identity()
        
        # Genererer nyt access token
        new_access_token = create_access_token(identity=current_user)
        
        return jsonify({"access_token": new_access_token}), 200
    except Exception as e:
        return jsonify({"error": "Unable to refresh token", "details": str(e)}), 401






