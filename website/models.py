from . import db
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.sql import func

class UserDB(db.Model, UserMixin):
    __tablename__ = "user_db"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password1: Mapped[str] = mapped_column(String(100), nullable=False)

    notes = relationship("Note", back_populates="user")


class Note(db.Model):
    __tablename__ = "note"
    id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    data: Mapped[str] = mapped_column(String(100000), nullable=True)
    date: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=func.now())

    # Create Foreign Key, "users.id" - referes to the tablename of UserDB
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("user_db.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    user = relationship("UserDB", back_populates="notes")
