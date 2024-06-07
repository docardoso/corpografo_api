from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import get_jwt_identity

db = SQLAlchemy()

def jwt_filter_by(model, **criteria):
    return db.session.query(model).filter_by(user_id=get_jwt_identity(), **criteria)
