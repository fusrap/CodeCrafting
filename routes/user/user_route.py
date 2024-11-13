from flask import Blueprint, jsonify, request
from routes.base_route import BaseRoute
from flasgger import Swagger, swag_from

user_bp = Blueprint('user_bp', __name__)

class UserRoutes(BaseRoute):

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
