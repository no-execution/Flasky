from flask import Blueprint

api = Blueprint('api',__name__)

from . import comments,authentication,decorators,errors,users,posts