from datetime import timedelta
from flask import Flask
from flask_smorest import Api
import os
from flask_jwt_extended import JWTManager
import uuid
import secrets

from db import db

import models

from resources import CorpusBlueprint, DocumentBlueprint, UserBlueprint

def create_app(db_url=None):
    app = Flask(__name__)

    app.config['PROPAGATE_EXCEPTIONS'] = True

    app.config['API_TITLE'] = 'Corpografo REST API'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.1.0'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv('DATABASE_URL', 'sqlite:///data.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'echo': True}

    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', str(secrets.SystemRandom().getrandbits(2**8)))
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = os.getenv('ACCESS_EXPIRES', timedelta(days=1))

    db.init_app(app)

    with app.app_context():
        db.create_all()

    api = Api(app)

    api.register_blueprint(CorpusBlueprint)
    api.register_blueprint(DocumentBlueprint)
    api.register_blueprint(UserBlueprint)

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def is_jwt_revoked(jwt_header, jwt_payload):
        return db.session.get(models.RevokedJWTModel, jwt_payload['jti']) is not None

    return app

if __name__ == '__main__':
    create_app().run(debug=True, ssl_context='adhoc')
