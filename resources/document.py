from flask_smorest import Blueprint
from flask.views import MethodView

from db import db
from models import DocumentModel
from schemas import DocumentSchema
from security import login_required

blp = Blueprint("Documents", __name__, description="Operations on documents")

@blp.route("/document/<int:document_id>")
class DocumentPicker(MethodView):
    @blp.response(200, DocumentSchema)
    def get(self, document_id):
        return DocumentModel.get_or_404(document_id)

    def delete(self, document_id):
        db.session.delete(DocumentModel.get_or_404(document_id))
        db.session.commit()
        return {'message': 'Document deleted'}

    @blp.arguments(DocumentSchema)
    @blp.response(200, DocumentSchema)
    def put(self, document_data, document_id):
        document = DocumentModel.get_or_404(document_id)

        for k in document_data:
            setattr(document, k, document_data[k])

        db.session.add(document)
        db.session.commit()
        return document

@blp.route("/document")
class Document(MethodView):
    @blp.arguments(DocumentSchema)
    @blp.response(201, DocumentSchema)
    def post(self, document_data):
        document = DocumentModel(**document_data)
        db.session.add(document)
        db.session.commit()
        return document