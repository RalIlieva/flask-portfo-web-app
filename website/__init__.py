from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
import os
from os import path
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_ckeditor import CKEditor
import logging
from logging.handlers import RotatingFileHandler
from config import Config
from flask_mail import Mail


# A must to avoid problems with migrations, esp. constraints and con-names
metadata = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
})


class Base(DeclarativeBase):
    metadata=metadata
db = SQLAlchemy(model_class=Base)
DB_NAME = 'website.db'
migrate = Migrate(render_as_batch=True, compare_type=True)
mail = Mail()
bootstrap = Bootstrap5()
ckeditor = CKEditor()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    bootstrap.init_app(app)
    ckeditor.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from .views import views
    from website.views.forms import NoteForm, CreatePostForm, Comment, EmptyForm

    from website.errors import bp as error_bp
    app.register_blueprint(error_bp)

    from website.auth.auth import auth as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/')

    from website.views.views import views
    app.register_blueprint(views, url_prefix='/')

    from .models import UserDB, Note, BlogPost, Comments, followers

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.get_or_404(UserDB, user_id)

        # Logging to a file setup
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/website.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Website startup')

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')


from website import models
