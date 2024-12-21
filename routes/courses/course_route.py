from flask_cors import cross_origin
from flask_restx import Namespace, Resource, fields, abort
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from database import db
from models import Course, CourseElement, TextElement, InputElement

api = Namespace('course', description='Course-related operations')


course_element_model = api.model('CourseElement', {
    "type": fields.String(description="The type of the element (e.g., 'Text' or 'Input')"),
    "text": fields.String(description="Text content for text elements", required=False),
    "label": fields.String(description="Label for input elements", required=False),
    "answer": fields.String(description="Answer for input elements", required=False)
})

course_create_model = api.model('Course', {
    'courseTitle': fields.String(required=True, description='The course title'),
    'courseDescription': fields.String(description='The course description'),
    'elements': fields.List(fields.Nested(course_element_model), description='A list of course elements')
})

course_model = api.model('CourseResponse', {
    "id": fields.Integer(description="The unique identifier of the course"),
    "courseTitle": fields.String(description="The title of the course"),
    "courseDescription": fields.String(description="A brief description of the course"),
    "created": fields.String(description="The creation timestamp of the course")
})

courses_model = api.model('CoursesResponse', {
    "courses": fields.List(fields.Nested(course_model), description="List of all courses")
})

def add_text_element(text):
    text_element = TextElement(
        text_=text
    )
    db.session.add(text_element)
    db.session.flush()
    return text_element.text_element_id


def add_input_element(label, answer):
    input_element = InputElement(
        label=label,
        answer=answer
    )
    db.session.add(input_element)
    db.session.flush()
    return input_element.input_element_id


@api.route('')
class CourseResource(Resource):
    @api.expect(course_create_model)
    @api.doc(
        description="Create a new course",
        responses={
            201: "Course created successfully",
            400: "Invalid input data",
            500: "An error occurred while creating the course"
        }
    )
    @cross_origin()
    def post(self):
        """
        Create a new course.
        """
        try:
            data = api.payload
            print(f"Received course data: {data}")

            if not isinstance(data.get('elements', []), list):
                abort(400, "Elements should be a list.")

            new_course = Course(
                course_title=data.get('courseTitle'),
                course_description=data.get('courseDescription')
            )
            db.session.add(new_course)
            db.session.flush()

            elements = data.get('elements', [])
            for element in elements:
                if 'type' not in element or element['type'] not in ['Text', 'Input']:
                    abort(400, f"Invalid element type: {element.get('type')}")

                if element['type'] == 'Text':
                    element_id = add_text_element(element.get('text', ''))
                elif element['type'] == 'Input':
                    element_id = add_input_element(element.get('label', ''), element.get('answer', ''))

                course_element = CourseElement(
                    course_id=new_course.course_id,
                    element_id=element_id,
                    element_type=element['type']
                )
                db.session.add(course_element)

            db.session.commit()

            course_data = {
                "id": new_course.course_id,
                "courseTitle": new_course.course_title,
                "courseDescription": new_course.course_description,
                "elements": elements
            }
            return {
                "message": "Course created successfully",
                "course": course_data
            }, 201

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {e}")
            return {
                "error": "An error occurred while creating the course"
            }, 500

        except Exception as e:
            print(f"Error creating course: {e}")
            return {
                "error": "An unexpected error occurred"
            }, 500

    @api.doc(
        description="Fetch all courses",
        responses={
            200: ("A list of all courses", courses_model),
            500: "An error occurred while fetching courses"
        }
    )
    @cross_origin()
    def get(self):
        """
        Fetch all courses.
        """
        try:
            courses = db.session.query(Course).all()
            serialized_courses = [
                {
                    "id": course.course_id,
                    "courseTitle": course.course_title,
                    "courseDescription": course.course_description,
                    "created": course.created.strftime('%Y-%m-%d %H:%M:%S') if course.created else None
                }
                for course in courses
            ]

            return {"courses": serialized_courses}, 200

        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return {"error": "An error occurred while fetching courses"}, 500

        except Exception as e:
            print(f"Error fetching courses: {e}")
            return {"error": "An unexpected error occurred"}, 500
        


@api.route('/<int:course_id>')
class CourseById(Resource):

    @api.doc(
        description="Retrieve a course by its ID, including its content elements",
        params={"course_id": "The ID of the course to retrieve"},
        responses={
            200: "Course retrieved successfully",
            404: "Course not found",
            500: "An error occurred while retrieving the course"
        }
    )
    @cross_origin()
    def get(self, course_id):
        """
        Retrieve a course by its ID, including its content elements.
        """
        try:
            # Hent kursusdata
            course = db.session.query(Course).filter_by(course_id=course_id).first()

            if not course:
                return {"error": f"Course with ID {course_id} not found"}, 404

            # Hent tilknyttede elementer fra CourseElement
            course_elements = db.session.query(CourseElement).filter_by(course_id=course_id).all()

            elements_data = []
            for course_element in course_elements:
                if course_element.element_type == 'Text':
                    # Hent tekstdata
                    text_element = db.session.query(TextElement).filter_by(text_element_id=course_element.element_id).first()
                    if text_element:
                        elements_data.append({
                            "id": course_element.course_element_id,
                            "type": "Text",
                            "isEditing": False,  # Du kan justere denne default værdi
                            "text": text_element.text_
                        })

                elif course_element.element_type == 'Input':
                    # Hent inputdata
                    input_element = db.session.query(InputElement).filter_by(input_element_id=course_element.element_id).first()
                    if input_element:
                        elements_data.append({
                            "id": course_element.course_element_id,
                            "type": "Input",
                            "isEditing": False,  # Du kan justere denne default værdi
                            "label": input_element.label,
                            "answer": input_element.answer
                        })

            # Serialiser kursusdataene
            course_data = {
                "id": course.course_id,
                "courseTitle": course.course_title,
                "courseDescription": course.course_description,
                "created": course.created.strftime('%Y-%m-%d %H:%M:%S') if course.created else None,
                "elements": elements_data  # Tilføj elementer til kursusdata
            }

            return {"message": "Course retrieved successfully", "course": course_data}, 200

        except SQLAlchemyError as e:
            print(f"Database error: {e}")
            return {"error": "An error occurred while retrieving the course"}, 500

        except Exception as e:
            print(f"Error retrieving course: {e}")
            return {"error": "An unexpected error occurred"}, 500



@api.route('/<int:course_id>')
class CourseResource(Resource):
    @api.doc(
        description="Delete a course by ID",
        params={"course_id": "The ID of the course to delete"},
        responses={
            200: "Course deleted successfully",
            404: "Course not found",
            500: "An error occurred while deleting the course"
        }
    )
    @cross_origin()
    def delete(self, course_id):
        """
        Delete a course by its ID using raw SQL.
        """
        try:
            course_exists_query = text("SELECT 1 FROM Course WHERE course_id = :course_id")
            result = db.session.execute(course_exists_query, {"course_id": course_id}).fetchone()

            if not result:
                return {"error": f"Course with ID {course_id} not found"}, 404

            delete_course_query = text("DELETE FROM Course WHERE course_id = :course_id")
            db.session.execute(delete_course_query, {"course_id": course_id})
            db.session.commit()

            return {"message": f"Course with ID {course_id} deleted successfully"}, 200

        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error: {e}")
            return {"error": "An error occurred while deleting the course"}, 500

        except Exception as e:
            print(f"Error deleting course: {e}")
            return {"error": "An unexpected error occurred"}, 500
