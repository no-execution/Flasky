from flask import jsonify,request
from app.models import Post
from app.exceptions import ValidationError
from . import api

def fobbiden(message):
    response = jsonify({'error':'fobbiden','message':message})
    response.status_code = 403
    return response

def unauthorized(message):
    response = jsonify({'error':'unauthorized','message':message})
    response.status_code = 401
    return response

def bad_request(message):
    response = jsonify({'error':'bad request','message':message})
    response.status_code = 400
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])

