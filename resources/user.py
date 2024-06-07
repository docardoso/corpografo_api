from time import time

from argon2 import PasswordHasher
from flask.views import MethodView
from flask_jwt_extended import create_access_token, get_jwt
from flask_smorest import Blueprint, abort

from db import db
from models import UserModel, RevokedJWTModel
from schemas import UserSchema, LoginSchema
from security import login_required

blp = Blueprint('Users', __name__, description='Operations on users')
ph = PasswordHasher()

@blp.route('/user/<int:user_id>')
class UserPicker(MethodView):
    @login_required(1)
    @blp.response(200, UserSchema)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)

    @login_required(2)
    def delete(self, user_id):
        db.session.delete(UserModel.query.get_or_404(user_id))
        db.session.commit()
        return {'message': 'User deleted'}

    @login_required(2)
    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    def put(self, user_data, user_id):
        user = UserModel.query.get_or_404(user_id)

        for i in user_data:
            setattr(user, i, user_data[i])

        db.session.add(user)
        db.session.commit()
        return user

@blp.route('/register')
class User(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        user_data['password'] = ph.hash(user_data['password'])
        user = UserModel(**user_data)
        db.session.add(user)
        db.session.commit()
        return user

@blp.route('/users')
class Users(MethodView):
    @login_required(2)
    @blp.response(200, LoginSchema(many=True))
    def get(self):
        return UserModel.query.all()

@blp.route('/login')
class Login(MethodView):
    @blp.arguments(LoginSchema)
    def post(self, login_data):
        user = UserModel.query.filter(
            UserModel.username == login_data['username']
            #& UserModel.password == pbkdf2_sha256.hash(login_data['passsword'])
        ).first()

        if user and ph.verify(user.password, login_data['password']):
            access_token = create_access_token(
                identity=user.id,
                additional_claims={'access_level': user.access_level}
            )
            return {'access_token': access_token}

        abort(401, message='Invalid credentials.')

@blp.route('/logout')
class Logout(MethodView):
    @login_required()
    def post(self):
        revoked_jwt = RevokedJWTModel(
            jti=get_jwt()['jti'],
            timestamp=time.time(),
        )
        db.session.add(revoked_jwt)
        db.session.commit()
        return {'revoked_jwt': revoked_jwt}
