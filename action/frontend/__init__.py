from flask import (
    Blueprint, render_template, request, redirect, url_for, session)

from sqlalchemy import exc

from action.utils import (
    authenticate, anonymous_only,
    login_user, LoginException, logout_user, redirect_back)

from action.models import (
    DBException, User, db, Movie, Recommendation, Favorite, Rating)

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


@frontend.route('/movies/recent/<int:limit>')
def recent_movies(limit):
    movies = Movie.query.order_by(
        Movie.last_modified.desc()).limit(limit).all()
    ifempty = 'No movies in our database yet! Check back later.'
    return render_template(
        'frontend_movie_cards.html', movies=movies, ifempty=ifempty)


@frontend.route('/movies/popular/<int:limit>')
def popular_movies(limit):
    movies = Movie.query.join(Rating).outerjoin(Favorite).order_by(
        Movie.avg_rating.desc(), Movie.favorite_count.desc()).all()
    ifempty = 'No rated movies in our database yet! Check back later.'
    return render_template(
        'frontend_movie_cards.html', movies=movies, ifempty=ifempty)


@frontend.route('/movies/recommended/<int:limit>')
@authenticate
def recommended_movies(limit):
    user_id = session['userId']
    movies = Movie.query.join(Recommendation).filter(
        Recommendation.user_id == user_id).order_by(
        Recommendation.created.desc(), Recommendation.predicted.desc()).all()
    ifempty = 'No recommendations for you yet! '\
              'Rate some movies to get started.'
    return render_template(
        'frontend_movie_cards.html', movies=movies, ifempty=ifempty)


@frontend.route('/movie/<int:movie_id>')
def movie(movie_id):
    movie = Movie.query.filter_by(id=movie_id).first()
    if movie is None:
        return 'Movie not found.', 404
    else:
        return render_template('frontend_movie.html', movie=movie)


@frontend.route('/movie/<int:movie_id>/favorite/add')
@authenticate
def fav_movie(movie_id):
    user_id = session['userId']
    try:
        favorite = Favorite(user_id=user_id, movie_id=movie_id)
        db.session.add(favorite)
        db.session.commit()
        return 'Success!', 200
    except exc.IntegrityError:
        return 'Cannot make this join.', 400


@frontend.route('/movie/<int:movie_id>/favorite/remove')
@authenticate
def unfav_movie(movie_id):
    user_id = session['userId']
    favorite = Favorite.query.filter_by(
        user_id=user_id, movie_id=movie_id).first()
    db.session.delete(favorite)
    db.session.commit()
    return 'Success!', 200


@frontend.route('/movies/favorites/<int:limit>')
@authenticate
def fav_movies(limit):
    user_id = session['userId']
    movies = Movie.query.join(Favorite).filter(
        Favorite.user_id == user_id).order_by(Favorite.created.desc()).all()
    return render_template(
        'frontend_movie_cards.html', movies=movies,
        ifempty='No favorite movies yet!')


@frontend.route('/movie/<int:movie_id>/rate/<int:value>')
@authenticate
def rate_movie(movie_id, value):
    user_id = session['userId']
    if value > 5:
        value = 5
    elif value < 1:
        value = 1
    try:
        old_rating = Rating.query.filter_by(
            user_id=user_id, movie_id=movie_id).first()
        if old_rating is not None:
            old_rating.value = value
        else:
            rating = Rating(user_id=user_id, movie_id=movie_id, value=value)
            db.session.add(rating)
        db.session.commit()
        return 'Success!', 200
    except exc.IntegrityError:
        return 'Could not rate this movie.', 400


@frontend.route('/profile')
@authenticate
def profile():
    user_id = session['userId']
    user = User.query.filter_by(id=user_id).first()
    return render_template('frontend_profile.html', user=user)


@frontend.route('/recommendations')
@authenticate
def recommendations():
    return render_template('frontend_recommendations.html')


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
