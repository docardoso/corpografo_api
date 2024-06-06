from flask_smorest import abort
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt

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