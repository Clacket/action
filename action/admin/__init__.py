from io import BytesIO
import datetime
import pyqrcode
from sqlalchemy import desc
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, flash)
from action.admin.utils import (
    authenticate, anonymous_only,
    activated_only, unactivated_only,
    login_admin, LoginException, logout_admin, login_admin_token)
from action.utils import redirect_back, upload_picture, UploadException
from action.models import (
    Admin, AdminInvite, Movie, Showing, Picture, DBException, db)


admin = Blueprint(
    'admin', __name__, subdomain='admin',
    template_folder='templates', static_folder='static')


@admin.route('/')
@authenticate
def index():
    return render_template('admin_index.html')


@admin.route('/login/1', methods=['GET', 'POST'])
@anonymous_only
def login():
    error = None
    if request.method == 'POST':
        try:
            login_admin(
                request.form['username'],
                request.form['password'])
            return redirect(url_for('admin.login_token'))
        except LoginException as e:
            error = str(e)
    return render_template('admin_login.html', error=error)


@admin.route('/login/2', methods=['GET', 'POST'])
@activated_only
def login_token():
    error = None
    if request.method == 'POST':
        token = request.form.get('token')
        try:
            login_admin_token(token)
            return redirect_back('admin.index')
        except LoginException as e:
            error = str(e)
    return render_template('admin_login_token.html', error=error)


@admin.route('/register/<invite_id>', methods=['GET', 'POST'])
@anonymous_only
def register(invite_id):
    invite = AdminInvite.query.filter_by(id=invite_id).first()
    error = None
    if request.method == 'GET':
        if invite is not None and invite.claimed is None:
            return render_template(
                'admin_register.html', email=invite.email,
                invite_id=invite_id, error=error)
        return 'Nope.', 404
    else:
        error = None
        if invite is not None and invite.claimed is None:
            try:
                invite.claimed = datetime.datetime.utcnow()
                username = request.form['username'].lower()
                password = request.form['password']
                password_confirm = request.form['password_confirm']
                email = invite.email.lower()
                admin = Admin(
                    username=username, password=password, email=email,
                    password_confirm=password_confirm)
                db.session.add(admin)
                db.session.commit()
                login_admin(username, password)
                return redirect(url_for('admin.activate'))
            except (DBException, LoginException) as e:
                error = str(e)
        else:
            error = 'This invite is invalid or no longer available.'
        return render_template(
            'admin_register.html', email=invite.email,
            invite_id=invite_id, error=error)


@admin.route('/two_factor', methods=['GET', 'POST'])
@unactivated_only
def activate():
    admin = Admin.query.filter_by(
            id=session.get('adminId'), two_factor=False).first()
    error = None
    if request.method == 'POST':
        try:
            login_admin_token(request.form.get('token'), force=True)
            admin.two_factor = True
            db.session.commit()
            return redirect(url_for('admin.index'))
        except LoginException as e:
            error = str(e)
    return render_template('admin_2fa.html', error=error), 200, {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@admin.route('/qr_code')
@unactivated_only
def qrcode():
    admin = Admin.query.filter_by(
        id=session.get('adminId'), two_factor=False).first()
    url = pyqrcode.create(admin.totp_uri)
    stream = BytesIO()
    url.svg(stream, scale=5, module_color='#0e0e0e', background='#ecf0f1')
    return stream.getvalue(), 200, {
        'Content-Type': 'image/svg+xml',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'}


@admin.route('/logout')
def logout():
    logout_admin()
    return redirect_back('admin.index')


@admin.route('/movies/recent/<int:limit>')
@authenticate
def recent_movies(limit):
    movies = Movie.query.outerjoin(Picture).order_by(
        desc(Movie.last_modified)).limit(limit).all()
    return render_template('admin_movie_cards.html', movies=movies)


@admin.route('/movie/new', methods=['POST'])
@authenticate
def add_movie():
    error = None
    kwargs = Movie.get_kwargs(request)
    movie = Movie(**kwargs)
    db.session.add(movie)
    if 'poster' in request.files and request.files['poster'].filename != '':
        try:
            db.session.flush()
            url = upload_picture(request.files['poster'])
            picture = Picture(movie_id=movie.id, url=url)
            db.session.add(picture)
        except UploadException as e:
            error = str(e)
    if error is None:
        db.session.commit()
        flash('Movie {0} added!'.format(kwargs.get('title')))
    else:
        flash(error)
    return redirect(url_for('admin.index'))


@admin.route('/movie/<int:movie_id>/edit', methods=['POST'])
@authenticate
def edit_movie(movie_id):
    error = None
    kwargs = Movie.get_kwargs(request)
    movie = Movie.query.filter_by(id=movie_id).first()
    if movie is None:
        return 'Movie not found.', 404
    if 'poster' in request.files and request.files['poster'].filename != '':
        try:
            db.session.flush()
            url = upload_picture(request.files['poster'])
            picture = Picture(movie_id=movie.id, url=url)
            db.session.add(picture)
        except UploadException as e:
            error = str(e)
    for kwarg, value in kwargs.items():
        setattr(movie, kwarg, value)
    if error is None:
        db.session.commit()
        flash('Movie {0} edited!'.format(kwargs.get('title')))
    else:
        flash(error)
    return redirect(url_for('admin.index'))


@admin.route('/movie/<int:movie_id>/delete', methods=['POST'])
@authenticate
def delete_movie(movie_id):
    movie = Movie.query.filter_by(id=movie_id).first()
    if movie is None:
        return 'Movie not found', 404
    title = movie.title
    db.session.delete(movie)
    db.session.commit()
    flash('Movie {0} deleted!'.format(title))
    return redirect(url_for('admin.index'))


@admin.route('/cinema/new', methods=['POST'])
@authenticate
def add_cinema():
    kwargs = Showing.get_kwargs(request)
    cinema = Showing(type='cinema', **kwargs)
    db.session.add(cinema)
    db.session.commit()
    flash('Cinema {0} added!'.format(kwargs.get('name')))
    return redirect(url_for('admin.index'))


@admin.route('/cinemas/recent/<int:limit>')
@authenticate
def recent_cinemas(limit):
    cinemas = Showing.query.filter_by(type='cinema').order_by(
        desc(Showing.last_modified)).limit(limit).all()
    return render_template('admin_cinema_cards.html', cinemas=cinemas)


@admin.route('/cinema/<int:cinema_id>/delete', methods=['POST'])
@authenticate
def delete_cinema(cinema_id):
    cinema = Showing.query.filter_by(id=cinema_id, type='cinema').first()
    if cinema is None:
        return 'Cinema not found', 404
    name = cinema.name
    db.session.delete(cinema)
    db.session.commit()
    flash('Cinema {0} deleted!'.format(name))
    return redirect(url_for('admin.index'))
