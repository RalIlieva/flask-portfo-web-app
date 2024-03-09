import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "Shall_hide_it_as_environ"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'website.db')
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is True
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'pthntstngml@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'broh fsjg mvzv enje'
    ADMINS = ['pthntstngml@gmail.com']
    # POSTS_PER_PAGE = 5