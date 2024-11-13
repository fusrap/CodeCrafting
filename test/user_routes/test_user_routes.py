import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from routes.user.user_route import UserRoutes

app = Flask(__name__)

def test_user_login_success():
    with app.app_context(), app.test_request_context():
        with patch('routes.user.user_route.request') as mock_request:
            mock_request.get_json = MagicMock(return_value={"username": "admin", "password": "admin"})
            response = UserRoutes.user_login()
            assert response[1] == 200
            assert response[0].json == {"success": True}

def test_user_login_missing_data():
    with app.app_context(), app.test_request_context():
        with patch('routes.user.user_route.request') as mock_request:
            mock_request.get_json = MagicMock(return_value={"username": "admin"})
            response = UserRoutes.user_login()
            assert response[1] == 400
            assert response[0].json == {"error": "Failed to login"}

def test_user_login_invalid_credentials():
    with app.app_context(), app.test_request_context():
        with patch('routes.user.user_route.request') as mock_request:
            mock_request.get_json = MagicMock(return_value={"username": "user", "password": "pass"})
            response = UserRoutes.user_login()
            assert response[1] == 401
            assert response[0].json == {"error": "Invalid credentials"}
