from . import mail
from flask_mail import Message
from flask import render_template

def send_mail(to,subject,template,**kwargs):
    msg = Message(subject,sender='flask_kaifa@sina.com',recipients=[to])
    msg.html = render_template(template+'.html',**kwargs)
    mail.send(msg)