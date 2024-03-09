from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Length, InputRequired, EqualTo, ValidationError
from website import db
from website.models import UserDB


class RegisterForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    email = EmailField(label='Email', validators=[Email(allow_empty_local=False)])
    password1 = PasswordField(label='Password', validators=[Length(min=8)])
    password2 = PasswordField(label='Confirm Password', validators=[Length(min=8)])
    submit = SubmitField(label='Register Me')

    def validate_name(self, name):
        if name.data != self.original_name:
            user = db.session.scalar((db.select(UserDB).where(UserDB.name == self.name.data)))
            #Also working - user = UserDB.query.filter_by(name=name.data).first()
            if user is not None:
                raise ValidationError('This username is already taken. Please choose a different name')


# LoginForm to login existing users
class LoginForm(FlaskForm):
    email = EmailField(label='Email', validators=[Email(allow_empty_local=False)])
    password = PasswordField(label='Password', validators=[Length(min=8)])
    submit = SubmitField(label='Log Me')


class ChangePassword(FlaskForm):
    password1 = PasswordField(label='Old Password', validators=[DataRequired()])
    password = PasswordField(label='New Password', validators=[InputRequired(), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField(label='Repeat Password')
    submit = SubmitField(label='Change Password')


class EditProfileForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    about_me = StringField(label="About Me", validators=[Length(min=0, max=150)])
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


class ResetPasswordRequestForm(FlaskForm):
    email = EmailField(label='Email', validators=[Email(allow_empty_local=False)])
    submit = SubmitField(label='Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField(label='Password', validators=[DataRequired()])
    password2 = PasswordField(label='Repeat Passowrd', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='Request Password Reset')