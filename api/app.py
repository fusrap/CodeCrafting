from flask import Flask, jsonify
from config import config
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from database import init_db, db
from sqlalchemy import text
from routes.kanban.board_routes import kanban_bp
import os


load_dotenv()

def create_app():
    config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    print("SQLALCHEMY_DATABASE_URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    app.register_blueprint(kanban_bp, url_prefix="/api/kanban")

    jwt = JWTManager(app)
    init_db(app) 

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

