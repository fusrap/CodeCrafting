import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv
from sqlalchemy import text
from database import init_db, db
from routes.user.user_route import user_bp
from flasgger import Swagger

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Determine environment
    env = os.getenv("FLASK_ENV", "development")
    print("ENV:" + env)

    # Set configuration based on environment
    if env == "development":
        app.config["DEBUG"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DEV_DATABASE_URL")
        print("Running in Development Environment")
    elif env == "production":
        app.config["DEBUG"] = True 
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("PROD_DATABASE_URL")
        print("Running in Production Environment")
    else:
        raise ValueError("Invalid FLASK_ENV. Please set it to 'development' or 'production'.")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1) 

    # Initialize extensions
    jwt = JWTManager(app)
    swagger = Swagger(app)
    init_db(app)

    # Register blueprint
    app.register_blueprint(user_bp)

    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print("Database connection successful")
        except Exception as e:
            print("Database connection failed:", e)

    return app

app = create_app()
