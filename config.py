import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "Shall_hide_it_as_environ"
    # POSTS_PER_PAGE = 5