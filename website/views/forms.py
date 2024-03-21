from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, URL
from flask_ckeditor import CKEditorField
from flask import request
from website import db
from website.models import UserDB


class NoteForm(FlaskForm):
    note = StringField(label='New Note', validators=[Length(min=10)])
    submit = SubmitField(label='Add')


class CreatePostForm(FlaskForm):
    title = StringField(label="Blog Post Title", validators=[DataRequired()])
    subtitle = StringField(label="Subtitle", validators=[DataRequired()])
    img_url = StringField(label="Blog Image URL", validators=[URL()])
    body = CKEditorField(label="Blog Content", validators=[DataRequired()])
    submit = SubmitField(label="Submit Post")


class Comment(FlaskForm):
    comment_text = CKEditorField(label="Comment", validators=[DataRequired()])
    submit = SubmitField(label="Submit Comment")


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class SearchForm(FlaskForm):
    q = StringField(label='Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)


class MessageForm(FlaskForm):
    message = TextAreaField(label='Message', validators=[DataRequired(), Length(min=0, max=150)])
    submit = SubmitField(label='Submit')