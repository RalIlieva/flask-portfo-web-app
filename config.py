import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "Shall_hide_it_as_environ"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'website.db')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') or 1
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL') is False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_AUTH_METHOD = 'PLAIN'  # Use PLAIN authentication
    ADMINS = ['pthntstngml@gmail.com']
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    if not ELASTICSEARCH_URL:
        ELASTICSEARCH_URL = os.environ.get('LOCAL_ELASTICSEARCH_URL', 'http://localhost:9200')
    POSTS_PER_PAGE = 4