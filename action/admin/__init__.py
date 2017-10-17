from io import BytesIO
import datetime
import pyqrcode
from flask import (
    Blueprint, render_template, request, redirect, url_for, session)
from action.admin.utils import (
    authenticate, anonymous_only,
    activated_only, unactivated_only,
    login_admin, LoginException, logout_admin, login_admin_token)
from action.utils import redirect_back
from action.models import Admin, AdminInvite, DBException, db


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
                email = invite.email.lower()
                admin = Admin(
                    username=username, password=password, email=email)
                db.session.add(admin)
                db.session.commit()
                login_admin(username, password)
                return redirect(url_for('admin.activate'))
            except (DBException, LoginException) as e:
                error = str(e)
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
