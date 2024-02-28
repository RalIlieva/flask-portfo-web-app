from . import db
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.sql import func
from hashlib import md5

class UserDB(db.Model, UserMixin):
    __tablename__ = "user_db"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password1: Mapped[str] = mapped_column(String(100), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(db.Boolean, default=False)  # New field

    notes = relationship("Note", back_populates="user")

    posts = relationship("BlogPost", back_populates="author")

    comments = relationship("Comments", back_populates="comment_author")

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


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