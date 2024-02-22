from flask import Blueprint, render_template, request, url_for, flash, jsonify, redirect
from flask_login import login_required, current_user
from .forms import NoteForm
from .models import Note, UserDB
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', current_user=current_user)


@views.route('/my-profile', methods=['GET', 'POST'])
@login_required
def myprofile():
    form = NoteForm()

    if form.validate_on_submit():
        data = form.note.data

        new_note = Note(
            data=data,
            user_id=current_user.id
        )
        db.session.add(new_note)
        db.session.commit()
        flash('Note added!', category='success')

        # Clear the form data after successful submission
        form.note.data = ''  # Reset the note field

    return render_template('profile.html', form=form, current_user=current_user)


@views.route('/delete-note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note_to_delete = db.get_or_404(Note, note_id)
    # Additional check
    if note_to_delete.user_id == current_user.id:
        db.session.delete(note_to_delete)
        db.session.commit()
        flash('Note deleted!', category='success')
    else:
        flash('You don\'t have permission to delete!', category='error')
    return redirect(url_for('views.myprofile'))



@views.route('/blog', methods=['GET', 'POST'])
@login_required
def blog():
    return render_template('blog.html', current_user=current_user)