from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Length, URL, InputRequired, EqualTo, ValidationError
from flask_ckeditor import CKEditorField
from . import db
from .models import UserDB


class RegisterForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    email = EmailField(label='Email', validators=[Email(allow_empty_local=False)])
    password1 = PasswordField(label='Password', validators=[Length(min=8)])
    password2 = PasswordField(label='Confirm Password', validators=[Length(min=8)])
    submit = SubmitField(label='Register Me')


# LoginForm to login existing users
class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[Email(allow_empty_local=False)])
    password = PasswordField(label='Password', validators=[Length(min=8)])
    submit = SubmitField(label='Log Me', render_kw={"class": "btn btn-primary"})


class EditProfileForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    submit = SubmitField(label='Edit')

    def __init__(self, original_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_name = original_name

    def validate_name(self, name):
        if name.data != self.original_name:
            user = db.session.scalar((db.select(UserDB).where(UserDB.name == self.name.data)))
            #Also working - user = UserDB.query.filter_by(name=name.data).first()
            if user is not None:
                raise ValidationError('This username is already taken. Please choose a different name')


class ChangePassword(FlaskForm):
    password1 = PasswordField(label='Old Password', validators=[DataRequired()])
    password = PasswordField(label='New Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField(label='Repeat Password')
    submit = SubmitField(label='Change Password')

class NoteForm(FlaskForm):
    note = StringField(label='New Note', validators=[Length(min=10)])
    submit = SubmitField(label='Add')


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class Comment(FlaskForm):
    comment_text = CKEditorField(label="Comment", validators=[DataRequired()])
    submit = SubmitField(label="Submit Comment")
