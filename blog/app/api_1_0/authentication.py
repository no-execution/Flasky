from flask_httpauth import HTTPBasicAuth
from .errors import unauthorized,fobbiden
from app.models import AnonymousUser,User
from flask import g,jsonify
from . import api

auth = HTTPBasicAuth()

#用户登录验证，返回一个布尔值
@auth.verify_password
def verify_password(email_or_token,password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email = email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized('错误的认证信息')

@api.before_request
@auth.login_required
def befor_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return fobbiden('账户未认证')

@api.route('/token')
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.token.used:
        return unauthorized('invalid token')
    return jsonify({'token':g.current_user.generate_auth_token(expiration=3600),'expiration':3600})

