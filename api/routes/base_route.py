from sqlalchemy.exc import SQLAlchemyError
from database import db

class BaseRoute:
    
    model = None

    def create(self, data):
        try: 
            instance = self.model(**data)
            db.session.add(instance)
            db.session.commit()
            return instance
        except SQLAlchemyError as err:
            db.session.rollback()
            return {"error": str(err)}, 500
        
    def get_all(self):
        try:
            with db.session() as session:
                instances = session.query(self.model).all()
                return instances, 200
        except SQLAlchemyError as e:
            return {"error": str(e)}, 500
