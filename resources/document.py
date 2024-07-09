from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity

from db import db
from models import Document, User, DocumentsUsers
from schemas import DocumentSchema, PlainDocumentSchema
from util import login_required, get_current_user, get_user_document

from sqlalchemy.exc import IntegrityError

blp = Blueprint("Documents", __name__, description="Operations on documents")

@blp.route("/document/<int:document_id>")
class DocumentPicker(MethodView):
    @login_required()
    @blp.response(200, DocumentSchema)
    def get(self, document_id):
        return get_user_document(document_id)

    #def delete(self, document_id):
    #    db.session.delete(Document.get_or_404(document_id))
    #    db.session.commit()
    #    return {'message': 'Document deleted'}

    #@blp.arguments(DocumentSchema)
    #@blp.response(200, DocumentSchema)
    #def put(self, document_data, document_id):
    #    document = Document.get_or_404(document_id)

    #    for k in document_data:
    #        setattr(document, k, document_data[k])

    #    db.session.add(document)
    #    db.session.commit()
    #    return document

@blp.route("/document")
class DocumentMethodView(MethodView):
    @login_required()
    @blp.arguments(PlainDocumentSchema)
    @blp.response(201, PlainDocumentSchema)
    def post(self, document_data):
        document = Document(**document_data)
        document.users.append(get_current_user())
        db.session.add(document)
        try:
            db.session.commit()
        except IntegrityError as e:
            #db.session.rollback()
            abort(400, message=e._message()) #  'The name of each document must be unique.')  # 

        return document

    @login_required()
    @blp.response(200, PlainDocumentSchema(many=True))
    def get(self):
        return get_current_user().documents

@blp.route('/document/<int:document_id>/user/<user_email>')
class DocumentUserEmail(MethodView):
    @login_required()
    def post(self, document_id, user_email):
        get_user_document(document_id)
        user_id = db.session.query(User).filter_by(email=user_email).first().id
        db.session.add(DocumentsUsers(document_id=document_id, user_id=user_id))
        db.session.commit()

        return {'message': 'Document shared with user'}

@blp.route('/document/<int:document_id>/user/<int:user_id>')
class DocumentUserId(MethodView):
    @login_required()
    def delete(self, document_id, user_id):
        get_user_document(document_id)
        db.session.delete(
            db.session.query(DocumentsUsers).get({
                'document_id': document_id,
                'user_id': user_id,
            })
        )
        db.session.commit()

        return {'message': 'Document unshared with user'}