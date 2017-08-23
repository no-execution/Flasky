from . import api
from .errors import fobbiden
from .. import db
from flask import g,request,jsonify,url_for,current_app
from app.models import Post,User,Permission
from app.decorators import permission_required

#暂时理解为request中包括json数据，服务器接受request，经过操作再返回一个json数据
@api.route('/posts/',methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_post():
    post = Post.from_json(request.json)
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json()),201,{'Location':url_for('api.get_post',id=post.id,_external=True)}

@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(
        page, per_page=10,
        error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=page+1, _external=True)
    return jsonify({
        'posts': [post.to_json() for post in posts],
        'prev': prev,
        'next': next,
        'count': pagination.total})

@api.route('/posts/<int:id>')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())

@api.route('/posts/<int:id>')
@permission_required(Permission.WRITE_ARTICLES)
def edit_post():
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMINISTER):
        return fobbiden('权限不够')
    post.body = request.json.get('body',post.body)
    db.session.add(post)
    db.session.commit()
    return jsonify(post.to_json())