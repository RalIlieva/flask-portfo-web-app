from flask import Blueprint, render_template, request, url_for, flash, jsonify, redirect
from flask_login import login_required, current_user
from .forms import NoteForm, CreatePostForm, Comment, EmptyForm
from .models import Note, BlogPost, Comments, UserDB
from . import db
import json
from datetime import date


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html', current_user=current_user)


@views.route('/profile/<name>', methods=['GET', 'POST'])
@login_required
def myprofile(name):
    user = UserDB.query.filter_by(name=name).first()
    if not user:
        # Handle case where user with given name doesn't exist
        flash('User not found!', category='error')
        return redirect(url_for('views.home'))
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

    # Show all own and following posts on my profile.
    # When viewing other profile - show only the posts of the user
    page = request.args.get('page', 1, type=int)
    posts = user.posts
    # query_posts = user.posts
    # posts = query_posts.paginate(page=page, per_page=3, error_out=False)
    # next_url = url_for('views.myprofile', name=user.name, page=posts.next_num) \
    #         if posts.has_next else None
    # prev_url = url_for('views.myprofile', name=user.name, page=posts.prev_num)\
    #     if posts.has_prev else None

    query_comments = Comments.query.filter_by(author_id=user.id)
    comments = db.paginate(query_comments, page=page, max_per_page=4, error_out=False)
    next_url = url_for('views.myprofile', name=user.name, page=comments.next_num)\
        if comments.has_next else None
    prev_url = url_for('views.myprofile',name=user.name, page=comments.prev_num)\
        if comments.has_prev else None

    followform = EmptyForm()

    return render_template('profile.html', form=form, current_user=current_user,
                           user=user, posts=posts, comments=comments, followform=followform,
                           next_url=next_url, prev_url=prev_url)

    # Version 1
    # posts = user.posts
    #
    # comments = user.comments
    #
    # followform = EmptyForm()
    #
    # return render_template('profile.html', form=form, current_user=current_user,
    #                        user=user, posts=posts, comments=comments, followform=followform)

    # Version 2
    # Show all own and following posts on my profile.
    # When viewing other profile - show only the posts of the user
    # page = request.args.get('page', 1, type=int)
    # if user == current_user:
    #     posts = db.session.scalars(current_user.following_posts()).all()
    # else:
    #     posts = user.posts
    #
    # comments = user.comments
    #
    # followform = EmptyForm()
    #
    # return render_template('profile.html', form=form, current_user=current_user,
    #                        user=user, posts=posts, comments=comments, followform=followform)


    # Version 3
    # page = request.args.get('page', 1, type=int)
    # if user == current_user:
    #     query_posts = current_user.following_posts()
    # else:
    #     query_posts = user.posts
    #
    # posts = db.paginate(query_posts, page=page, per_page=3, error_out=False)
    #
    # next_url = url_for('views.myprofile', name=user.name, page=posts.next_num)\
    #     if posts.has_next else None
    # prev_url = url_for('views.myprofile', name=user.name, page=posts.prev_num)\
    #     if posts.has_prev else None
    #
    # query_comments = Comments.query.filter_by(author_id=user.id)
    # comments = db.paginate(query_comments, page=page, max_per_page=4, error_out=False)
    # next_url = url_for('views.myprofile', name=user.name, page=comments.next_num)\
    #     if posts.has_next else None
    # prev_url = url_for('views.myprofile',name=user.name, page=comments.prev_num)\
    #     if posts.has_prev else None

    # followform = EmptyForm()
    #
    # return render_template('profile.html', form=form, current_user=current_user,
    #                        user=user, posts=posts, comments=comments, followform=followform)
                           # next_url=next_url, prev_url=prev_url)


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
    return redirect(url_for('views.myprofile', name=current_user.name))


@views.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = db.select(BlogPost).order_by(BlogPost.date.desc())
    posts = db.paginate(posts, page=page, per_page=2, error_out=False)
    next_url = url_for('views.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('views.explore', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template("blog.html", all_posts=posts, current_user=current_user,
                           next_url=next_url, prev_url=prev_url)


# Blog
@views.route('/blog', methods=['GET', 'POST'])
@login_required
def blog_all_posts():
    # result = db.session.execute(db.select(BlogPost))
    # posts = result.scalars().all()
    # page = request.args.get('page', 1, type=int)
    posts = db.session.scalars(current_user.following_posts()).all()
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
        return redirect(url_for("views.show_post", post_id=requested_post.id))
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


@views.route("/delete/comment/<int:comment_id>/<int:post_id>")
@login_required
def delete_comment(post_id, comment_id):
    post_to_delete = db.get_or_404(Comments, comment_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("views.show_post", post_id=post_id, current_user=current_user))


@views.route('/follow/<name>', methods=['POST'])
@login_required
def follow(name):
    followform = EmptyForm()
    if followform.validate_on_submit():
        user = db.session.scalar(
            db.select(UserDB).where(UserDB.name == name))
        if user is None:
            flash(f'User {name} not found.')
            return redirect(url_for('views.blog_all_posts'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('views.myprofile', name=name))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are following {name}!')
        return redirect(url_for('views.myprofile', name=name))
    else:
        return redirect(url_for('views.blog_all_posts'))


@views.route('/unfollow/<name>', methods=['POST'])
@login_required
def unfollow(name):
    followform = EmptyForm()
    if followform.validate_on_submit():
        user = db.session.scalar(
            db.select(UserDB).where(UserDB.name == name))
        if user is None:
            flash(f'User {name} not found.')
            return redirect(url_for('views.blog_all_posts'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('views.myprofile', name=name))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You are not following {name}.')
        return redirect(url_for('views.myprofile', name=name))
    else:
        return redirect(url_for('views.blog_all_posts'))