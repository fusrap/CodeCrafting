import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv
from flask_restx import Api
from sqlalchemy import text
from database import init_db, db
from routes.user.user_route import user_bp
from routes.courses.course_route import api as course_namespace
from routes.games.jeopardy_route import api as jeopardy_namespace
from routes.courses.course_enrollment_route import api as course_enrollment_api
from flasgger import Swagger

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True) 

    env = os.getenv("FLASK_ENV", "development")
    print("ENV:" + env)

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
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=1) 

    jwt = JWTManager(app)
    swagger = Swagger(app)
    init_db(app)

    app.register_blueprint(user_bp)

    api = Api(
    app,
    version='1.0',
    title='Learning API',
    description='',
    doc='/newdocs'
    )
    
    api.add_namespace(course_namespace, path='/course')
    api.add_namespace(jeopardy_namespace, path='/jeopardy')
    api.add_namespace(course_enrollment_api, path='/course/enrollment')
    

    with app.app_context():
        try:
            db.session.execute(text('SELECT 1'))
            print("Database connection successful")
        except Exception as e:
            print("Database connection failed:", e)

    return app

app = create_app()
