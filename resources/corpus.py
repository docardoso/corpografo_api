import collections as cl
from sqlalchemy.orm import joinedload
from flask_jwt_extended import get_jwt_identity
from nltk.util import everygrams
from flask_smorest import Blueprint, abort
from flask.views import MethodView

from sqlalchemy.exc import IntegrityError

from db import db
from models import Corpus, UsersCorpora, CorporaDocuments, User
from schemas import CorpusSchema, PlainCorpusSchema
from util import login_required, get_current_user, get_user_corpus, get_user_document

blp = Blueprint('Corpora', __name__, description='Operations on corpora')

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
    @blp.response(201, PlainCorpusSchema)
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
    @blp.response(200, CorpusSchema)
    def get(self, corpus_id):
        return get_user_corpus(corpus_id)

    #@login_required()
    #def delete(self, corpus_id):
    #    db.session.delete(get_user_corpus(corpus_id))
    #    db.session.commit()
    #    return {'message': 'Corpus deleted'}

    #@login_required()
    #@blp.arguments(PlainCorpusSchema)
    #@blp.response(200, PlainCorpusSchema)
    #def put(self, corpus_data, corpus_id):
    #    corpus = get_user_corpus(corpus_id)

    #    for i in corpus_data:
    #        setattr(corpus, i, corpus_data[i])

    #    db.session.add(corpus)
    #    db.session.commit()
    #    return corpus

#@blp.route('/corpus/<int:corpus_id>/documents')
#class CorpusDocuments(MethodView):
#    @login_required()
#    @blp.response(200, PlainDocumentSchema(many=True))
#    def get(self, corpus_id):
#        return get_user_corpus(corpus_id).documents

@blp.route('/corpus/<int:corpus_id>/document/<int:document_id>')
class CorpusUser(MethodView):
    @login_required()
    def post(self, corpus_id, document_id):
        get_user_corpus(corpus_id)
        get_user_document(document_id)
        db.session.add(CorporaDocuments(corpus_id=corpus_id, document_id=document_id))
        db.session.commit()

        return {'message': 'Document added to corpus'}

    @login_required()
    def delete(self, corpus_id, document_id):
        get_user_corpus(corpus_id)
        get_user_document(document_id)
        db.session.delete(
            db.session.query(CorporaDocuments).get({
                'corpus_id': corpus_id,
                'document_id': document_id
            })
        )
        db.session.commit()

        return {'message': 'Document removed from corpus'}

@blp.route('/corpus/<int:corpus_id>/user/<user_email>')
class CorpusUserEmail(MethodView):
    @login_required()
    def post(self, corpus_id, user_email):
        get_user_corpus(corpus_id)
        user_id = db.session.query(User).filter_by(email=user_email).first().id
        db.session.add(UsersCorpora(corpus_id=corpus_id, user_id=user_id))
        db.session.commit()

        return {'message': 'Corpus shared with user'}

@blp.route('/corpus/<int:corpus_id>/user/<int:user_id>')
class CorpusUserId(MethodView):
    @login_required()
    def delete(self, corpus_id, user_id):
        get_user_corpus(corpus_id)
        db.session.delete(
            db.session.query(UsersCorpora).get({
                'corpus_id': corpus_id,
                'user_id': user_id,
            })
        )
        db.session.commit()

        return {'message': 'Corpus unshared with user'}

@blp.route('/ngram/<int:corpus_id>/<int:min_len>/<int:max_len>/<case_sensitive>')
class Ngram(MethodView):
    @login_required()
    def get(self, corpus_id, min_len, max_len, case_sensitive):
        corpus = db.session.query(
            UsersCorpora
        ).options(
            joinedload(
                UsersCorpora.corpus
            ).joinedload(
                Corpus.document_relations
            ).joinedload(
                CorporaDocuments.document
            )
        ).get_or_404({
            'corpus_id':corpus_id,
            'user_id':get_jwt_identity(),
        }).corpus

        if case_sensitive == 'False':
            return [corpus.name, cl.Counter(' '.join(j) for i in corpus.documents for j in everygrams(i.content.lower().split(), min_len, max_len))]

        return [corpus.name, cl.Counter(' '.join(j) for i in corpus.documents for j in everygrams(i.content.split(), min_len, max_len))]