from functools import wraps
from flask import g
from .errors import fobbiden

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            if not g.current_user.can(permission):
                return fobbiden('权限不够')
            return f(*args,**kwargs)
        return decorated_function
    return decorator