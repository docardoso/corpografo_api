from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity

from sqlalchemy.exc import IntegrityError

from db import db, jwt_filter_by
from models import CorpusModel, DocumentModel
from schemas import CorpusSchema, PlainCorpusSchema, PlainDocumentSchema
from security import login_required

blp = Blueprint('Corpora', __name__, description='Operations on corpora')

@blp.route('/corpora')
class Corpus(MethodView):
    @login_required(2)
    @blp.response(200, CorpusSchema(many=True))
    def get(self):
        return CorpusModel.query.all()

@blp.route('/corpus')
class Corpus(MethodView):
    @login_required()
    @blp.response(200, PlainCorpusSchema(many=True))
    def get(self):
        return jwt_filter_by(CorpusModel).all()

    @login_required()
    @blp.arguments(PlainCorpusSchema)
    @blp.response(201, CorpusSchema)
    def post(self, corpus_data):
        corpus = CorpusModel(**corpus_data)
        corpus.user_id = get_jwt_identity()
        db.session.add(corpus)
        try:
            db.session.commit()
        except IntegrityError:
            abort(400, message='The name of each corpus must be unique.')
        return corpus

@blp.route('/corpus/<int:corpus_id>')
class CorpusPicker(MethodView):
    @login_required()
    @blp.response(200, PlainCorpusSchema)
    def get(self, corpus_id):
        return jwt_filter_by(CorpusModel, id=corpus_id).first_or_404()

    @login_required()
    def delete(self, corpus_id):
        #db.session.delete(CorpusModel.query.filter_by(id=corpus_id, user_id=get_jwt_identity()).first_or_404())
        db.session.delete(jwt_filter_by(CorpusModel, id=corpus_id).first_or_404())
        db.session.commit()
        return {'message': 'Corpus deleted'}

    @login_required()
    @blp.arguments(PlainCorpusSchema)
    @blp.response(200, PlainCorpusSchema)
    def put(self, corpus_data, corpus_id):
        corpus = jwt_filter_by(CorpusModel, id=corpus_id).first_or_404()

        for i in corpus_data:
            setattr(corpus, i, corpus_data[i])

        db.session.add(corpus)
        db.session.commit()
        return corpus

@blp.route('/corpus/<int:corpus_id>/documents')
class CorpusDocuments(MethodView):
    @login_required()
    @blp.response(200, PlainDocumentSchema(many=True))
    def get(self, corpus_id):
        #return DocumentModel.query.filter_by(id=corpus_id, user_id=get_jwt_identity()).first_or_404()
        corpus = jwt_filter_by(CorpusModel, id=corpus_id).first_or_404()
        return corpus.documents
