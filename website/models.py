from . import db
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import relationship, Mapped, mapped_column, WriteOnlyMapped
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.sql import func
from hashlib import md5
from typing import Optional
from datetime import datetime, timezone
from time import time
import jwt
from flask import current_app
from werkzeug.security import generate_password_hash
from website.search import add_to_index, remove_from_index, query_index
import json


class SearchableMixin(object):
    __indexname__ = None  # Define this attribute in subclasses
    @classmethod
    def search(cls, expression, page, per_page):
        index_name = cls.__indexname__  # Get the index name
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return [], 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.session.scalars(query), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)


db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user_db.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user_db.id'), primary_key=True)
)

class UserDB(db.Model, UserMixin):
    __tablename__ = "user_db"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password1: Mapped[str] = mapped_column(String(100), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)  # New field
    about_me: Mapped[Optional[str]] = mapped_column(String(150))
    last_seen: Mapped[Optional[datetime]] = mapped_column(default=lambda: datetime.now(timezone.utc))
    last_message_read_time: so.Mapped[Optional[datetime]]

    notes = relationship("Note", back_populates="user")

    posts: WriteOnlyMapped['BlogPost'] = relationship("BlogPost", back_populates="author")

    comments = relationship("Comments", back_populates="comment_author")

    following: WriteOnlyMapped['UserDB'] = relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: WriteOnlyMapped['UserDB'] = relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    messages_sent: so.WriteOnlyMapped['Message'] = so.relationship(
        foreign_keys='Message.sender_id', back_populates='author')
    messages_received: so.WriteOnlyMapped['Message'] = so.relationship(
        foreign_keys='Message.recipient_id', back_populates='recipient')

    notifications: so.WriteOnlyMapped['Notification'] = so.relationship(
        back_populates='user')


    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(UserDB.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)

    def following_posts(self):
        Author = so.aliased(UserDB)
        Follower = so.aliased(UserDB)
        return (
            sa.select(BlogPost)
            .join(BlogPost.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(BlogPost)
            .order_by(BlogPost.date.desc())
        )

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return db.session.get(UserDB, id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def unread_message_count(self):
        last_read_time = self.last_message_read_time or datetime(1900, 1, 1)
        query = sa.select(Message).where(Message.recipient == self,
                                         Message.timestamp > last_read_time)
        return db.session.scalar(sa.select(sa.func.count()).select_from(
            query.subquery()))


    def add_notification(self, name, data):
        db.session.execute(self.notifications.delete().where(
            Notification.name == name))
        n = Notification(name=name, payload_json=json.dumps(data), user=self)
        db.session.add(n)
        return n


class Note(db.Model):
    __tablename__ = "note"
    id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[str] = mapped_column(String(100000), nullable=True)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Create Foreign Key, "users.id" - referes to the tablename of UserDB
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user_db.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    user = relationship("UserDB", back_populates="notes")


class BlogPost(SearchableMixin, db.Model):
    __tablename__ = "blog_posts"
    __searchable__ = ['title', 'subtitle', 'body']
    __indexname__ = "blog_posts"  # Specify the Elasticsearch index name
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Create Foreign Key, "users.id" - referes to the tablename of USerDB
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user_db.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    author = relationship("UserDB", back_populates="posts")

    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=True)

#     Parent BlogPost - Child Comments relationship
    comments = relationship("Comments", back_populates="parent_post")


class Comments(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

#     Creating child relationship UserDB - Comments
# "user_db.id" - refers to the tablename of UserDB class
# "comments" refer to the comments property of the UserDB class
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user_db.id"))
    comment_author = relationship("UserDB", back_populates="comments")

#     Creating child relationship BlogPost - Comments
    post_id: Mapped[str] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False)


class Message(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(sa.ForeignKey(UserDB.id), index=True)
    recipient_id: Mapped[int] = mapped_column(sa.ForeignKey(UserDB.id), index=True)
    body: Mapped[str] = mapped_column(sa.String(140))
    timestamp: Mapped[datetime] = mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

    author: Mapped[UserDB] = relationship(
        foreign_keys='Message.sender_id',
        back_populates='messages_sent')
    recipient: Mapped[UserDB] = relationship(
        foreign_keys='Message.recipient_id',
        back_populates='messages_received')

    def __repr__(self):
        return '<Message {}>'.format(self.body)


class Notification(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128), index=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(UserDB.id),
                                               index=True)
    timestamp: so.Mapped[float] = so.mapped_column(index=True, default=time)
    payload_json: so.Mapped[str] = so.mapped_column(sa.Text)

    user: so.Mapped[UserDB] = so.relationship(back_populates='notifications')

    def get_data(self):
        return json.loads(str(self.payload_json))
