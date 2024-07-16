from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint, abort
from util import login_required, get_current_user, get_user_document
from flask.views import MethodView
from schemas import LanguageSchema, PlainLanguageSchema
from models import Language
from db import db
from sqlalchemy.exc import IntegrityError

blp = Blueprint("Languages", __name__, description="Operations on languages")

@blp.route("/language")
class LanguageMethodView(MethodView):
    @login_required()
    @blp.arguments(PlainLanguageSchema)
    @blp.response(201, PlainLanguageSchema)
    def post(self, language_data):
        language = Language(**language_data)
        language.user_id = get_jwt_identity()
        #language.user = get_current_user()
        db.session.add(language)
        try:
            db.session.commit()
        except IntegrityError as e:
            #db.session.rollback()
            abort(400, message=e._message()) #  'The name of each document must be unique.')  # 

        return language

    @login_required()
    @blp.response(200, PlainLanguageSchema(many=True))
    def get(self):
        return get_current_user().languages

@blp.route("/language/<int:language_id>")
class LanguagePicker(MethodView):
    @login_required()
    @blp.response(200, LanguageSchema)
    def get(self, language_id):
        return db.first_or_404(
            db.session.query(Language).filter_by(
                id=language_id,
                user_id=get_jwt_identity(),
            )
        )

    @login_required()
    @blp.arguments(PlainLanguageSchema)
    @blp.response(200, PlainLanguageSchema)
    def put(self, language_data, language_id):
        language = db.first_or_404(
            db.session.query(Language).filter_by(
                id=language_id,
                user_id=get_jwt_identity(),
            )
        )

        for i in language_data:
            setattr(language, i, language_data[i])

        db.session.add(language)
        db.session.commit()
        return language