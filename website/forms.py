from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Length, URL, InputRequired, EqualTo
from flask_ckeditor import CKEditorField


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


class ChangePassword(FlaskForm):
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
