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

    notes = relationship("Note", back_populates="user")

    posts = relationship("BlogPost", back_populates="author")

    comments = relationship("Comments", back_populates="comment_author")

    following: WriteOnlyMapped['UserDB'] = relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: WriteOnlyMapped['UserDB'] = relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

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
            .order_by(BlogPost.timestamp.desc())
        )


class Note(db.Model):
    __tablename__ = "note"
    id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[str] = mapped_column(String(100000), nullable=True)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Create Foreign Key, "users.id" - referes to the tablename of UserDB
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user_db.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    user = relationship("UserDB", back_populates="notes")


class BlogPost(db.Model):
    __tablename__ = "blog_posts"
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

