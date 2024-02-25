from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .forms import RegisterForm, LoginForm, EditProfileForm, ChangePassword
from .models import UserDB, Note
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        result = db.session.execute(db.select(UserDB).where(UserDB.email == email))
        user = result.scalar()
        # If the email is not found, then asking the user to try again
        if not user:
            flash('That email does not exist, please try again.', category='error')
            return redirect(url_for('auth.login'))
        #     Check if the stored hash password is the same entered hashed password
        elif not check_password_hash(user.password1, password):
            flash('Wrong password. Please try again.', category='error')
            return redirect(url_for('auth.login'))
        #   If all checks are ok, then email = email in the database, the hashed pass = hashed pass in the database
        #     = > good to go & log in
        else:
            login_user(user)
            return redirect(url_for('views.myprofile', name=current_user.name))

    return render_template('login.html', form=form, current_user=current_user)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Firstly - checking if the email is already registered in the DB
        email = form.email.data
        password1 = form.password1.data
        password2 = form.password2.data
        result = db.session.execute(db.select(UserDB).where(UserDB.email == email))
        user = result.scalar()
        if user:
            flash('This email has already been registered. Please Log in.', category='error')
            return redirect(url_for('auth.login'))
        # Secondly, if password1 equals password 2
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        # Thirdly, if the email no existing in the DB = > hashing & saving it
        else:
            hashed_pass = generate_password_hash(
            password=form.password1.data,
            method='pbkdf2:sha256',
            salt_length=8,
            )
            new_user = UserDB(
                name=form.name.data,
                email=form.email.data,
                password1=hashed_pass,
            )

            db.session.add(new_user)
            db.session.commit()
            flash('Successful registration!', category='success')
            return redirect(url_for('auth.login'))
    return render_template('register.html', form=form, current_user=current_user)


@auth.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        db.session.commit()
        flash('Your changes have been saved.', category='success')
        return redirect(url_for('auth.edit_profile'))
    elif request.method == 'GET':
        form.name.data = current_user.name
    return render_template('edit_profile.html', form=form, current_user=current_user)


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePassword()
    if form.validate_on_submit():
        if check_password_hash(current_user.password1, form.password1.data):
            new_hashed_pass = generate_password_hash(
                password=form.password.data,
                method='pbkdf2:sha256',
                salt_length=8,
            )
            current_user.password1 = new_hashed_pass
            db.session.commit()
            flash('Your new password has been saved.')
        else:
            flash('Your old password is not correct', category='error')
    elif request.method == 'GET':
        form.password.data = current_user.password1
    return render_template('change_password.html', form=form, current_user=current_user)


