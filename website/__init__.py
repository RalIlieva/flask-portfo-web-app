from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
from os import path
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar


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



def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "Shall_hide_it_as_environ"
    bootstrap = Bootstrap5(app)
    ckeditor = CKEditor(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    migrate = Migrate(app, db)

    from .auth import auth
    from .views import views
    from .forms import RegisterForm, LoginForm, NoteForm, CreatePostForm, Comment, EditProfileForm, ChangePassword

    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(views, url_prefix='/')

    from .models import UserDB, Note, BlogPost, Comments

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.get_or_404(UserDB, user_id)

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
