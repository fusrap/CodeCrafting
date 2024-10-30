from flask import Flask, jsonify
from config import config
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from database import init_db, db
from sqlalchemy import text
import os


load_dotenv()

def create_app():
    config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    print("SQLALCHEMY_DATABASE_URI:", app.config.get("SQLALCHEMY_DATABASE_URI"))

    jwt = JWTManager(app)
    init_db(app) 

    @app.route("/test-db", methods=["GET"])
    def test_db():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify({"message": "Database connection successful!"}), 200
        except Exception as e:
            return jsonify({"message": f"Database connection error: {e}"}), 500


    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

