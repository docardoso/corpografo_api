from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint, abort
from util import login_required, get_current_user, get_user_document
from flask.views import MethodView
from schemas import AuthorSchema, PlainAuthorSchema
from models import Author, AuthorsDocuments
from db import db
from sqlalchemy.exc import IntegrityError

blp = Blueprint("Authors", __name__, description="Operations on authors")

@blp.route("/author")
class AuthorMethodView(MethodView):
    @login_required()
    @blp.arguments(PlainAuthorSchema)
    @blp.response(201, PlainAuthorSchema)
    def post(self, author_data):
        author = Author(**author_data)
        author.user_id = get_jwt_identity()
        #author.user = get_current_user()
        db.session.add(author)
        try:
            db.session.commit()
        except IntegrityError as e:
            #db.session.rollback()
            abort(400, message=e._message()) #  'The name of each document must be unique.')  # 

        return author

    @login_required()
    @blp.response(200, PlainAuthorSchema(many=True))
    def get(self):
        return get_current_user().authors

@blp.route("/author/<int:author_id>")
class AuthorPicker(MethodView):
    @login_required()
    @blp.response(200, AuthorSchema)
    def get(self, author_id):
        return db.first_or_404(
            db.session.query(Author).filter_by(
                id=author_id,
                user_id=get_jwt_identity(),
            )
        )

    @login_required()
    @blp.arguments(PlainAuthorSchema)
    @blp.response(200, PlainAuthorSchema)
    def put(self, author_data, author_id):
        author = db.first_or_404(
            db.session.query(Author).filter_by(
                id=author_id,
                user_id=get_jwt_identity(),
            )
        )

        for i in author_data:
            setattr(author, i, author_data[i])

        db.session.add(author)
        db.session.commit()
        return author

@blp.route('/author/<int:author_id>/document/<int:document_id>')
class AuthorUser(MethodView):
    @login_required()
    def post(self, author_id, document_id):
        db.first_or_404(db.session.query(Author).filter_by(
            id=author_id,
            user_id=get_jwt_identity(),
        ))

        get_user_document(document_id)

        db.session.add(AuthorsDocuments(author_id=author_id, document_id=document_id))
        db.session.commit()

        return {'message': 'Document and author linked'}

    @login_required()
    def delete(self, author_id, document_id):
        db.first_or_404(db.session.query(Author).filter_by(
            id=author_id,
            user_id=get_jwt_identity(),
        ))

        get_user_document(document_id)

        db.session.delete(
            db.session.query(AuthorsDocuments).get_or_404({
                'author_id': author_id,
                'document_id': document_id
            })
        )
        db.session.commit()

        return {'message': 'Document and author unlinked'}
