import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from sqlalchemy import text
from database import init_db, db
from routes.kanban.board_routes import kanban_bp

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)

    # Determine environment
    env = os.getenv("FLASK_ENV", "development")
    print("ENV:" + env)

    # Set configuration based on environment
    if env == "development":
        app.config["DEBUG"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DEV_DATABASE_URL")
        print("Running in Development Environment")
    elif env == "production":
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("PROD_DATABASE_URL")
        print("Running in Production Environment")
    else:
        raise ValueError("Invalid FLASK_ENV. Please set it to 'development' or 'production'.")

    # Common configuration
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # Initialize extensions
    jwt = JWTManager(app)
    init_db(app)

    # Register blueprint
    app.register_blueprint(kanban_bp, url_prefix="/kanban")

    # Test the database connection on startup
    with app.app_context():
        try:
            # Use text('SELECT 1') for the raw SQL execution
            db.session.execute(text('SELECT 1'))
            print("Database connection successful")
        except Exception as e:
            print("Database connection failed:", e)

    if env == "development":
        app.run()

    return app

app = create_app()
