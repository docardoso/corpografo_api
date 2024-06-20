from time import time

from sqlalchemy.exc import IntegrityError

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask.views import MethodView
from flask_jwt_extended import create_access_token, get_jwt_identity
from flask_smorest import Blueprint, abort

from db import db
from models import User, Corpus, Document
from schemas import UserSchema, LoginSchema
from util import login_required, revoke_jwt

blp = Blueprint('Users', __name__, description='Operations on users')
ph = PasswordHasher()

@blp.route('/user/<int:user_id>')
class UserPicker(MethodView):
    @login_required(1)
    @blp.response(200, UserSchema)
    def get(self, user_id):
        return User.query.get_or_404(user_id)

    @login_required(2)
    def delete(self, user_id):
        db.session.delete(User.query.get_or_404(user_id))
        Corpus.query.filter(~Corpus.users.any()).delete()
        Document.query.filter(~Document.users.any()).delete()

        if get_jwt_identity() == user_id:
            revoke_jwt(False)

        db.session.commit()

        return {'message': 'User deleted'}

    @login_required(2)
    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        user = User.query.get_or_404(user_id)

        for i in user_data:
            setattr(user, i, user_data[i])

        db.session.add(user)
        db.session.commit()
        return user

@blp.route('/register')
class Register(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        user_data['password'] = ph.hash(user_data['password'])
        user = User(**user_data)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=e._message())
        return user

@blp.route('/users')
class Users(MethodView):
    @login_required(2)
    @blp.response(200, LoginSchema(many=True))
    def get(self):
        return User.query.all()

@blp.route('/login')
class Login(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, login_data):
        user = User.query.filter(
            User.email == login_data['email']
            #& UserModel.password == pbkdf2_sha256.hash(login_data['password'])
        ).first()

        if not user:
            abort(401, message='Invalid credentials')

        try:
            ph.verify(user.password, login_data['password'])
        except VerifyMismatchError:
            abort(401, message='Invalid credentials')

        access_token = create_access_token(
            identity=user.id,
            additional_claims={'access_level': user.access_level}
        )
        return {
            'access_token': access_token,
            'name': user.name
        }


@blp.route('/logout')
class Logout(MethodView):
    @login_required()
    def post(self):
        revoke_jwt()
        return {'message': 'Logout successful'}