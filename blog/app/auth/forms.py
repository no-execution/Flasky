from flask_wtf import Form
from wtforms import StringField, SubmitField,PasswordField,BooleanField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(Form):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm (Form):
    email = StringField('Email',validators=[Required(),Length(1,64),Email()])
    username = StringField('Username',validators=[Required(),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,
                                                                    'Usernames must have only letters,'
                                                                    'numbers,dots or underscores')])
    password = PasswordField('Password',validators=[Required(),EqualTo('password2',message='Passwords must match')])
    password2 = PasswordField('Confirm Password',validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username has been used')

class MailForm(Form):
    usermail = StringField('注册邮箱',validators=[Required(),Length(1,64)])
    submit = SubmitField('确定')

class ResetForm(Form):
    resetpassword = PasswordField('新的密码',validators=[Required(),EqualTo('resetpassword2',message='密码必须一致')])
    resetpassword2 = PasswordField('确认密码',validators=[Required()])
    submit = SubmitField('确认')

class ConfirmPasswordForm(Form):
    password = PasswordField('请输入密码',validators=[Required(),Length(1,64)])
    submit = SubmitField('确定')
