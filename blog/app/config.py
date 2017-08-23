import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'hard to guess string'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flask_kaifa@sina.com>'
    FLASKY_ADMIN = 'whtqsq@126.com'

    @staticmethod
    def init_app(app):
        pass
class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.sina.com'
    MAIL_PORT = 25 #电子邮件服务器的端口
    MAIL_USERNAME = 'flask_kaifa@sina.com'
    MAIL_PASSWORD = 'wht941202'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config = {'development':DevelopmentConfig,
          'testing':TestingConfig,
          'production':ProductionConfig,
          'default':DevelopmentConfig
          }
