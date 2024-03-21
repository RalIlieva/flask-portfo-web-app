from flask import render_template, request, url_for, flash, redirect, current_app, g
from flask_login import login_required, current_user
from website.models import Note, BlogPost, Comments, UserDB, Message, Notification
from website import db
from datetime import date
from website.views import views
from website.views.forms import NoteForm, CreatePostForm, Comment, EmptyForm, SearchForm, MessageForm
from datetime import datetime, timezone


@views.before_app_request
def before_request():
    if current_user.is_authenticated:
        g.search_form = SearchForm()

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
    query = user.posts.select().order_by(BlogPost.date.desc())
    posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('views.myprofile', name=user.name, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('views.myprofile', name=user.name, page=posts.prev_num)\
        if posts.has_prev else None

    query_comments = Comments.query.filter_by(author_id=user.id)
    comments = db.paginate(query_comments, page=page, max_per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('views.myprofile', name=user.name, page=comments.next_num)\
        if comments.has_next else None
    prev_url = url_for('views.myprofile', name=user.name, page=comments.prev_num)\
        if comments.has_prev else None

    followform = EmptyForm()

    return render_template('views/profile.html', form=form, current_user=current_user,
                           user=user, posts=posts.items, comments=comments.items, followform=followform,
                           next_url=next_url, prev_url=prev_url)


@views.route('/profile/<name>/popup')
@login_required
def user_popup(name):
    user = db.first_or_404(db.select(UserDB).where(UserDB.name == name))
    form = EmptyForm()
    return render_template('user_popup.html', user=user, form=form)


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
    posts = db.paginate(posts, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('views.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('views.explore', page=posts.prev_num) \
        if posts.has_prev else None

    return render_template("views/blog.html", all_posts=posts, current_user=current_user,
                           next_url=next_url, prev_url=prev_url)


@views.route('/blog', methods=['GET', 'POST'])
@login_required
def blog_all_posts():
    page = request.args.get('page', 1, type=int)
    followed_posts = db.paginate(current_user.following_posts(), page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('views.blog_all_posts', page=followed_posts.next_num) \
        if followed_posts.has_next else None
    prev_url = url_for('views.blog_all_posts', page=followed_posts.prev_num) \
        if followed_posts.has_prev else None
    return render_template("views/blog.html", all_posts=followed_posts, current_user=current_user, is_follow=True,
                           next_url=next_url, prev_url=prev_url)


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
    return render_template("views/post.html", post=requested_post, current_user=current_user, form=comment_form)


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
    return render_template("views/make-post.html", form=form, current_user=current_user)


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
    return render_template("views/make-post.html", form=edit_form, is_edit=True, current_user=current_user)

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


@views.route('/search')
@login_required
def search():
    user = current_user
    if not g.search_form.validate():
        return redirect(url_for('views.explore'))
    page = request.args.get('page', 1, type=int)
    posts, total = BlogPost.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
    next_url = url_for('views.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
    prev_url = url_for('views.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
    return render_template('search.html', posts=posts, user=user,
                           next_url=next_url, prev_url=prev_url)


@views.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
    user = db.first_or_404(db.select(UserDB).where(UserDB.name == recipient))
    form = MessageForm()
    if form.validate_on_submit():
        msg = Message(author=current_user, recipient=user,
                      body=form.message.data)
        db.session.add(msg)
        user.add_notification('unread_message_count',
                              user.unread_message_count())
        db.session.commit()
        flash('Your message has been sent.')
        return redirect(url_for('views.myprofile', name=recipient))
    return render_template('send_message.html', form=form, recipient=recipient)


@views.route('/messages')
@login_required
def messages():
    current_user.last_message_read_time = datetime.now(timezone.utc)
    current_user.add_notification('unread_message_count', 0)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    query = current_user.messages_received.select().order_by(
        Message.timestamp.desc())
    messages = db.paginate(query, page=page,
                           per_page=current_app.config['POSTS_PER_PAGE'],
                           error_out=False)
    next_url = url_for('views.messages', page=messages.next_num) \
        if messages.has_next else None
    prev_url = url_for('views.messages', page=messages.prev_num) \
        if messages.has_prev else None
    return render_template('messages.html', messages=messages.items,
                           next_url=next_url, prev_url=prev_url, user=current_user)


@views.route('/notifications')
@login_required
def notifications():
    since = request.args.get('since', 0.0, type=float)
    query = current_user.notifications.select().where(
        Notification.timestamp > since).order_by(Notification.timestamp.asc())
    notifications = db.session.scalars(query)
    return [{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications]