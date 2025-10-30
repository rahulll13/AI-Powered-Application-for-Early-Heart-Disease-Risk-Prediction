# app/decorators.py

from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def doctor_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'Doctor':
            return {'message': 'Doctors access required!'}, 403 # 403 Forbidden status
        else:
            return fn(*args, **kwargs)
    return wrapper