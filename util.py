from flask_smorest import abort
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt, get_jwt_identity
from models import RevokedJWT
from db import db
import time
from models import User

def login_required(min_access_level=0):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            if get_jwt()['access_level'] >= min_access_level:
                return fn(*args, **kwargs)

            abort(403, message='Higher access level required for security clearance.')

        return decorator

    return wrapper

def revoke_jwt():
    revoked_jwt = RevokedJWT(
        jti=get_jwt()['jti'],
        timestamp=time.time(),
    )
    db.session.add(revoked_jwt)

    #return revoked_jwt

def get_current_user():
    return db.session.query(User).get(get_jwt_identity())