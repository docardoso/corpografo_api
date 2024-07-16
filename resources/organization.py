from flask_jwt_extended import get_jwt_identity
from flask_smorest import Blueprint, abort
from util import login_required, get_current_user, get_user_document
from flask.views import MethodView
from schemas import OrganizationSchema, PlainOrganizationSchema
from models import Organization
from db import db
from sqlalchemy.exc import IntegrityError

blp = Blueprint("Organizations", __name__, description="Operations on organizations")

@blp.route("/organization")
class OrganizationMethodView(MethodView):
    @login_required()
    @blp.arguments(PlainOrganizationSchema)
    @blp.response(201, PlainOrganizationSchema)
    def post(self, organization_data):
        organization = Organization(**organization_data)
        organization.user_id = get_jwt_identity()
        #organization.user = get_current_user()
        db.session.add(organization)
        try:
            db.session.commit()
        except IntegrityError as e:
            #db.session.rollback()
            abort(400, message=e._message()) #  'The name of each document must be unique.')  # 

        return organization

    @login_required()
    @blp.response(200, PlainOrganizationSchema(many=True))
    def get(self):
        return get_current_user().organizations

@blp.route("/organization/<int:organization_id>")
class OrganizationPicker(MethodView):
    @login_required()
    @blp.response(200, OrganizationSchema)
    def get(self, organization_id):
        return db.first_or_404(
            db.session.query(Organization).filter_by(
                id=organization_id,
                user_id=get_jwt_identity(),
            )
        )

    @login_required()
    @blp.arguments(PlainOrganizationSchema)
    @blp.response(200, PlainOrganizationSchema)
    def put(self, organization_data, organization_id):
        organization = db.first_or_404(
            db.session.query(Organization).filter_by(
                id=organization_id,
                user_id=get_jwt_identity(),
            )
        )

        for i in organization_data:
            setattr(organization, i, organization_data[i])

        db.session.add(organization)
        db.session.commit()
        return organization
