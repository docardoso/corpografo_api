from flask_smorest import Blueprint, abort
from flask.views import MethodView

from sqlalchemy.exc import IntegrityError

from db import db
from models import CorpusModel, DocumentModel
from schemas import CorpusSchema, PlainCorpusSchema, PlainDocumentSchema

blp = Blueprint('Corpora', __name__, description='Operations on corpora')

@blp.route('/corpus')
class Corpus(MethodView):
    @blp.response(200, PlainCorpusSchema(many=True))
    def get(self):
        return CorpusModel.query.all()

    @blp.arguments(CorpusSchema)
    @blp.response(201, CorpusSchema)
    def post(self, corpus_data):
        corpus = CorpusModel(**corpus_data)
        db.session.add(corpus)
        try:
            db.session.commit()
        except IntegrityError:
            abort(400, message='The name of each corpus must be unique.')
        return corpus

@blp.route('/corpus/<int:corpus_id>')
class CorpusPicker(MethodView):
    @blp.response(200, CorpusSchema)
    def get(self, corpus_id):
        return CorpusModel.query.get_or_404(corpus_id)

    def delete(self, corpus_id):
        db.session.delete(CorpusModel.query.get_or_404(corpus_id))
        db.session.commit()
        return {'message': 'Corpus deleted'}

    @blp.arguments(CorpusSchema)
    @blp.response(200, CorpusSchema)
    def put(self, corpus_data, corpus_id):
        corpus = CorpusModel.query.get_or_404(corpus_id)

        for i in corpus_data:
            setattr(corpus, i, corpus_data[i])

        db.session.add(corpus)
        db.session.commit()
        return corpus

@blp.route('/corpus/<int:corpus_id>/documents')
class CorpusDocuments(MethodView):
    @blp.response(200, PlainDocumentSchema(many=True))
    def get(self, corpus_id):
        return DocumentModel.query.filter_by(corpus_id=corpus_id)