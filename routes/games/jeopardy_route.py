from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, abort
from sqlalchemy.exc import SQLAlchemyError
from database import db
from models import Jeopardy, JeopardyCells, Subjects

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
            print(f"Received Jeopardy data: {data}")

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

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {e}")
            return {"error": "An error occurred while creating the Jeopardy game"}, 500

        except Exception as e:
            print(f"Error creating Jeopardy game: {e}")
            return {"error": "An unexpected error occurred"}, 500
