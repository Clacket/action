import datetime
from flask import Blueprint, render_template, request
from action.admin.utils import (
    authenticate, anonymous_only, login_admin, LoginException)
from action.utils import redirect_back
from action.models import Admin, AdminInvite, DBException, db


admin = Blueprint(
    'admin', __name__, subdomain='admin',
    template_folder='templates', static_folder='static')


@admin.route('/')
@authenticate
def index():
    return render_template('admin_index.html')


@admin.route('/login', methods=['GET', 'POST'])
@anonymous_only
def login():
    error = None
    if request.method == 'POST':
        try:
            login_admin(
                request.form['username'],
                request.form['password'],
                request.form['token'])
            return redirect_back('admin.index')
        except LoginException as e:
            error = e.message
    return render_template('admin_login.html', error=error)


@admin.route('/register/<invite_id>', methods=['GET', 'POST'])
@anonymous_only
def register(invite_id):
    invite = AdminInvite.query.filter_by(id=invite_id).first()
    error = None
    if request.method == 'GET':
        if invite is not None:
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
                return render_template('admin_2fa.html')
            except (DBException, LoginException) as e:
                error = e.message
        return render_template(
            'admin_register.html', email=invite.email,
            invite_id=invite_id, error=error)
