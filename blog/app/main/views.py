from flask import render_template,abort,session,redirect,url_for,flash,request,make_response
from . import main
from flask_login import login_required,current_user
from app.decorators import admin_required,permission_required
from app.models import Permission,User,Role,Post,Follow,Comment
from .forms import EditProfileForm,EditProfileAdminForm,PostForm,CommentForm
from app import db

#在cookie中清空show_followed值，以显示所有用户的文章
@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','',max_age=30*24*60*60)
    return resp

#在cookie中添加show_followed以完成显示关注者文章功能
@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed','1',max_age=30*24*60*60)
    return resp

#首页（包括写博客，显示关注人的文章，显示登录用户的名字，分页）
@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if form.validate_on_submit() and current_user.can(Permission.WRITE_ARTICLES):
        post = Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('main.index'))
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed',''))
    if show_followed:
        query = current_user.followed_posts
    else:
            query = Post.query
    page = request.args.get('page',1,type=int)
    pagination = query.order_by(Post.timestamp.desc()).paginate(page,
                                                                     per_page=15,
                                                                     error_out=False)
    posts = pagination.items
    return render_template('index.html',form=form,posts=posts,pagination=pagination,show_followed=show_followed)

#权限测试
@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For admins only"

#权限测试
@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "for comment moderators"

#用户个人页面
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page',1,int)
    pagination = Post.query.filter_by(author_id=user.id).paginate(page,per_page=5,error_out=False)
    posts = pagination.items
    return render_template('user.html',user=user,posts=posts,pagination=pagination)

#用户资料修改（普通用户权限）
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('个人信息修改完毕')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form)

#用户资料修改（管理员权限）
@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated')
        return redirect(url_for('main.user',username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html',form=form)

#显示用户的文章内容（包括用户头像，用户名，文章内容，编辑按钮，详情页按钮,评论）
@main.route('/post/<int:id>',methods=['POST','GET'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        #post是Post类在Comment类中建立的回引（backref）同理author
        comment = Comment(body=form.body.data,post=post,author=current_user._get_current_object())
        db.session.add(comment)
        flash('已评论')
        return redirect(url_for('.post',id=post.id,page=-1))
    page = request.args.get('page',1,type=int)
    if page==-1:
        page = (post.comments.count() - 1)/10 + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(page,per_page=10,error_out=False)
    comments = pagination.items
    return render_template('post.html',posts=[post],form=form,comments=comments,pagination=pagination)

#修改文章按钮
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('修改成功！')
        return redirect(url_for('main.post',id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html',form=form)

#关注
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('invalid user')
        return redirect('main.index')
    if current_user.is_following(user):
        flash('您已关注该用户')
    current_user.follow(user)
    flash('已关注')
    return redirect(url_for('main.user',username=username))

#取关
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('invalid user')
        return redirect('main.index')
    if not user.is_followed_by(current_user):
        flash('您没有关注该用户')
        return redirect('main.user')
    current_user.unfollow(user)
    return redirect('main.index')

#显示用户粉丝
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('invalid user')
        return redirect('main.index')
    page = request.args.get('page',1,type=int)
    pagination = user.followers.paginate(page,per_page=5,error_out=False)
    follows = [{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followers.html',user=user,endpoint='.followers',
                           pagination=pagination,follows=follows)

#显示用户关注了谁
@main.route('/followed/<username>')
def followed(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('invalid user')
        return redirect('main.index')
    page = request.args.get('page',1,type=int)
    pagination = user.followed.paginate(page,per_page=5,error_out=False)
    follows = [{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
    return render_template('followed.html',user=user,pagination=pagination,follows=follows,endpoint='.followed')

#管理员管理评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page',1,type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(page,per_page=10,error_out=False)
    comments=pagination.items
    return render_template('moderate.html',comments=comments,pagination=pagination,page=page)

#隐藏/显示评论
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('main.moderate',page=request.args.get('page',1,type=int)))

@main.route('/moderate/disabled/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('main.moderate',page=request.args.get('page',1,type=int)))