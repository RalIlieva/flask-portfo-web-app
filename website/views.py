from flask import Blueprint, render_template, request, url_for, flash, jsonify, redirect
from flask_login import login_required, current_user
from .forms import NoteForm, CreatePostForm, Comment
from .models import Note, BlogPost, Comments
from . import db
import json
from datetime import date

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


# Blog
@views.route('/blog', methods=['GET', 'POST'])
@login_required
def blog_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("blog.html", all_posts=posts, current_user=current_user)


@views.route('/blog/<int:post_id>', methods=["GET", "POST"])
@login_required
def show_post(post_id):
    requested_post = db.get_or_404(BlogPost, post_id)
    # Adding the Comment Form
    comment_form = Comment()
    # Only logged in users can comment posts
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Please log in first to comment!")
            return redirect(url_for("auth.login"))

        new_comment = Comments(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post,
        )

        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("views.blog_all_posts"))
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form)


@views.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author_id=current_user.id,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("views.blog_all_posts"))
    return render_template("make-post.html", form=form, current_user=current_user)


@views.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("views.show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)

@views.route("/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('views.blog_all_posts'))