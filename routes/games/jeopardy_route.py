from flask import request
from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, abort
from sqlalchemy.exc import SQLAlchemyError
from database import db
from models import Jeopardy, JeopardyCells, Subjects
from sqlalchemy import text

api = Namespace('jeopardy', description='Jeopardy related operations')

jeopardy_create_model = api.model('JeopardyCreate', {
    'title': fields.String(required=True, description='The title of the Jeopardy game'),
    'description': fields.String(required=False, description='The description of the Jeopardy game'),
    'subjects': fields.List(fields.String, required=True, description='List of column subjects'),
    'grid': fields.List(fields.List(fields.Nested(api.model('JeopardyCell', {
        'value': fields.Integer(required=True, description='Point value of the cell'),
        'question': fields.String(required=True, description='The question'),
        'answer': fields.String(required=True, description='The answer')
    }))), required=True, description='2D array of cells')
})

@api.route('')
class JeopardyResource(Resource):
    @api.expect(jeopardy_create_model)
    @api.doc(
        description="Create a new Jeopardy game",
        responses={
            201: "Jeopardy game created successfully",
            400: "Invalid input data",
            500: "An error occurred while creating the Jeopardy game"
        }
    )
    @cross_origin()
    def post(self):
        """
        Create a new Jeopardy game.
        """
        try:
            data = api.payload
            new_jeopardy = Jeopardy(
                jeopardy_title=data['title'],
                jeopardy_description=data.get('description', '')
            )
            db.session.add(new_jeopardy)
            db.session.flush()

            for subject_name in data["subjects"]:
                new_subject = Subjects(
                    subject_name=subject_name,
                    subject_jeopardy_id=new_jeopardy.jeopardy_id
                )
                db.session.add(new_subject)

            for row_index, row in enumerate(data['grid']):
                for col_index, cell in enumerate(row):
                    new_cell = JeopardyCells(
                        jeopardy_cell_value=cell['value'],
                        jeopardy_cell_question=cell['question'],
                        jeopardy_cell_answer=cell['answer'],
                        RowNumber=row_index,
                        ColumnNumber=col_index,
                        jeopardy_cell_jeopardy_id=new_jeopardy.jeopardy_id
                    )
                    db.session.add(new_cell)

            db.session.commit()
            return {"message": "Jeopardy game created successfully"}, 201

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

    @api.doc(
        description="Retrieve all Jeopardy games",
        responses={200: "Successfully retrieved all Jeopardy games", 500: "Error occurred"}
    )
    @cross_origin()
    def get(self):
        """
        List all Jeopardy games.
        """
        try:
            jeopardy_games = db.session.query(
                Jeopardy.jeopardy_id,
                Jeopardy.jeopardy_title,
                Jeopardy.jeopardy_description,
                Jeopardy.created
            ).all()

            return {
                "jeopardy_games": [
                    {
                        "id": game.jeopardy_id,
                        "title": game.jeopardy_title,
                        "description": game.jeopardy_description,
                        "created": game.created.strftime('%Y-%m-%d %H:%M:%S') if game.created else None,
                    } for game in jeopardy_games
                ]
            }, 200
        except Exception as e:
            return {"error": str(e)}, 500
        

@api.route('/<int:jeopardy_id>')
class JeopardyByIdResource(Resource):
    @api.doc(
        description="Retrieve a Jeopardy game by ID",
        responses={
            200: "Jeopardy game retrieved successfully",
            404: "Jeopardy game not found",
            500: "Error occurred"
        }
    )
    @cross_origin()
    def get(self, jeopardy_id):
        """
        Retrieve a Jeopardy game by ID.
        """
        try:
            jeopardy = db.session.query(Jeopardy).filter_by(jeopardy_id=jeopardy_id).first()

            if not jeopardy:
                return {"error": "Jeopardy game not found"}, 404

            jeopardy_data = {
                "id": jeopardy.jeopardy_id,
                "title": jeopardy.jeopardy_title,
                "description": jeopardy.jeopardy_description,
                "created": jeopardy.created.strftime('%Y-%m-%d %H:%M:%S') if jeopardy.created else None,
                "subjects": [s.subject_name for s in jeopardy.Subjects],
                "grid": [
                    [
                        {
                            "value": cell.jeopardy_cell_value,
                            "question": cell.jeopardy_cell_question,
                            "answer": cell.jeopardy_cell_answer
                        } for cell in jeopardy.JeopardyCells if cell.RowNumber == row
                    ] for row in range(max(c.RowNumber for c in jeopardy.JeopardyCells) + 1)
                ]
            }

            return {"message": "Jeopardy game retrieved successfully", "jeopardy": jeopardy_data}, 200

        except Exception as e:
            return {"error": str(e)}, 500

    @api.doc(
        description="Delete a Jeopardy game by ID",
        responses={200: "Jeopardy game deleted", 404: "Not found", 500: "Error"}
    )
    @cross_origin()
    def delete(self, jeopardy_id):
        """
        Delete a Jeopardy game by ID using raw SQL.
        """
        try:
            result = db.session.execute(
                text("DELETE FROM Jeopardy WHERE jeopardy_id = :jeopardy_id"),
                {"jeopardy_id": jeopardy_id}
            )
            db.session.commit()

            if result.rowcount == 0:
                return {"error": "Jeopardy game not found"}, 404

            return {"message": "Jeopardy game deleted"}, 200

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 500

       
