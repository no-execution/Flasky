from flask import render_template,redirect,request,url_for,flash
from . import auth
from flask_login import login_user,logout_user,login_required
from app.models import User,Permission
from .forms import LoginForm,RegistrationForm,MailForm,ResetForm,ConfirmPasswordForm
from app import db
from ..email import send_mail
from flask_login import current_user
from app.decorators import admin_required,permission_required

@auth.route('/login',methods=['GET','Post'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('invalid username or password')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logged out')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,username=form.username.data,password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail('flask_kaifa@sina.com', 'Confirm Your Account', 'auth/email/confirm', token=token, user=user)
         #参数1为收件人，参数2为主题，参数3为渲染模板，剩余参数为模板中的变量，导入模板，因此
        #confirm.html模板中将出现user与token变量，msg.body名为confirm.txt
        flash('A Confirmation email has been sent to you by email')
        flash('you can now login')
        return redirect(url_for('main.index'))
    return render_template('auth/registerform.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail('flask_kaifa@sina.com', 'Confirm Your Account', 'auth/email/confirm', token=token, user=current_user)
    flash('A Confirmation email has been sent to you by email')
    return redirect(url_for('main.index'))

@auth.route('/passwordlose',methods=['GET','POST'])
def passwordlose():
    form = MailForm()
    mail = form.usermail.data
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.usermail.data).first()
        if user is not None:
            token = user.generate_confirmation_token()
            send_mail(user.email,'Confirm','auth/email/resetmail',token=token,mail=mail)
            flash('确认邮件已经发往您的邮箱，请进入邮箱进行密码重置')
            return redirect(url_for('main.index'))
        flash('该邮箱账户不存在')
    return render_template('auth/passwordlose.html',form=form)

@auth.route('reset/<mail>/<token>',methods=['GET','POST'])
def reset(mail,token):
    form = ResetForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=mail).first()
        user.password = form.resetpassword.data
        db.session.commit()
        flash('密码修改成功！')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset.html',form=form)

@auth.route('/confirm-password',methods=['GET','POST'])
@login_required
def confirm_password():
    form = ConfirmPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user.verify_password(form.password.data):
                return redirect(url_for('auth.change_password'))
    return render_template('auth/prechange.html',form=form)

@auth.route('/change_password',methods=['GET','POST'])
@login_required
def change_password():
    form = ResetForm()
    if form.validate_on_submit():
        current_user.password = form.resetpassword.data
        db.session.commit()
        flash('密码修改成功')
        return redirect(url_for('main.index'))
    return render_template('auth/reset.html',form=form)








