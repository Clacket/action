from flask import Blueprint, render_template, request, redirect, url_for

from action.utils import (
    authenticate, anonymous_only,
    login_user, LoginException, logout_user, redirect_back)

from action.models import DBException, User, db

frontend = Blueprint(
    'frontend', __name__, static_folder='static',
    static_url_path='/frontend/static',
    template_folder='templates')


@frontend.route('/')
def index():
    return render_template('frontend_index.html')


@frontend.route('/cinemas')
def cinemas():
    return render_template('frontend_cinemas.html')


@frontend.route('/login', methods=['GET', 'POST'])
@anonymous_only
def login():
    error = None
    if request.method == 'POST':
        try:
            login_user(
                request.form['username'].lower(),
                request.form['password'])
            return redirect_back('frontend.index')
        except LoginException as e:
            error = str(e)
    return render_template('frontend_login.html', error=error)


@frontend.route('/register', methods=['GET', 'POST'])
@anonymous_only
def register():
    error = None
    if request.method == 'POST':
        try:
            username = request.form['username'].lower()
            password = request.form['password']
            password_confirm = request.form['password_confirm']
            email = request.form['email'].lower()
            user = User(
                username=username, password=password, email=email,
                password_confirm=password_confirm)
            db.session.add(user)
            db.session.commit()
            login_user(username, password)
            return redirect(url_for('frontend.index'))
        except (DBException, LoginException) as e:
            error = str(e)
    return render_template(
        'frontend_register.html', error=error)


@frontend.route('/logout')
@authenticate
def logout():
    logout_user()
    return redirect_back('frontend.index')
