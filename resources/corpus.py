from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity

from sqlalchemy.exc import IntegrityError

from db import db
from models import Corpus, User, UsersCorpora
from schemas import CorpusSchema, PlainCorpusSchema, PlainDocumentSchema
from util import login_required, get_current_user

blp = Blueprint('Corpora', __name__, description='Operations on corpora')

def get_user_corpus(corpus_id):
    return db.session.query(UsersCorpora).get_or_404({
        'corpus_id':corpus_id,
        'user_id':get_jwt_identity(),
    }).corpus

@blp.route('/corpora')
class Corpora(MethodView):
    @login_required(2)
    @blp.response(200, CorpusSchema(many=True))
    def get(self):
        return Corpus.query.all()

@blp.route('/corpus')
class CorpusView(MethodView):
    @login_required()
    @blp.response(200, PlainCorpusSchema(many=True))
    def get(self):
        return get_current_user().corpora

    @login_required()
    @blp.arguments(PlainCorpusSchema)
    @blp.response(201, CorpusSchema)
    def post(self, corpus_data):
        corpus = Corpus(**corpus_data)
        corpus.users.append(get_current_user())
        db.session.add(corpus)
        try:
            db.session.commit()
        except IntegrityError as e:
            #db.session.rollback()
            abort(400, message=e._message()) #  'The name of each corpus must be unique.')  # 

        return corpus

@blp.route('/corpus/<int:corpus_id>')
class CorpusPicker(MethodView):
    @login_required()
    @blp.response(200, PlainCorpusSchema)
    def get(self, corpus_id):
        return get_user_corpus(corpus_id)

    @login_required()
    def delete(self, corpus_id):
        db.session.delete(get_user_corpus(corpus_id))
        db.session.commit()
        return {'message': 'Corpus deleted'}

    @login_required()
    @blp.arguments(PlainCorpusSchema)
    @blp.response(200, PlainCorpusSchema)
    def put(self, corpus_data, corpus_id):
        corpus = get_user_corpus(corpus_id)

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
        return get_user_corpus(corpus_id).documents

@blp.route('/corpus/<int:corpus_id>/user/<int:user_id>')
class CorpusUser(MethodView):
    @login_required()
    def post(self, corpus_id, user_id):
        get_user_corpus(corpus_id)
        db.session.add(UsersCorpora(corpus_id=corpus_id, user_id=user_id))
        db.session.commit()

        return {'message': 'Corpus shared with user'}

    @login_required()
    def delete(self, corpus_id, user_id):
        get_user_corpus(corpus_id)

        db.session.delete(
            db.session.query(UsersCorpora).get_or_404({
                'corpus_id':corpus_id,
                'user_id':user_id,
            })
        )

        db.session.commit()

        return {'message': 'Corpus unshared with user'}
