from flask import Blueprint

auth = Blueprint('auth', __name__)

from website.auth import auth
