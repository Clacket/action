from flask import (
    Blueprint, render_template, request, redirect, url_for, session)

from action.utils import (
    authenticate, anonymous_only,
    login_user, LoginException, logout_user, redirect_back)

from action.models import DBException, User, db, Movie, Recommendation

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


@frontend.route('/browse')
def browse():
    return render_template('frontend_browse.html')


@frontend.route('/profile')
@authenticate
def profile():
    user_id = session['userId']
    user = User.query.filter_by(id=user_id).first()
    return render_template('frontend_profile.html', user=user)


@frontend.route('/recommendations')
@authenticate
def recommendations():
    user_id = session['userId']
    movies = Movie.query.join(Recommendation).filter(
        Recommendation.user_id == user_id).order_by(
        Recommendation.created.desc(), Recommendation.predicted.desc()).all()
    return render_template('frontend_recommendations.html', movies=movies)


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


@frontend.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    words = query.split(' ')
    like = '%' + '%'.join([w for w in words]) + '%'
    movies = Movie.query.filter(Movie.title.ilike(like)).all()
    return render_template('frontend_results.html', movies=movies, query=query)
