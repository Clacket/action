from flask import redirect, url_for, request, session
from functools import wraps

from action.models import Admin


def authenticate(f):
    """Decorator function to ensure user is logged in before a page is visited.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'adminId' in session and not user_activated():
            return redirect(url_for('admin.activate', next=request.url))
        if not is_logged_in() or not user_exists():
            logout_admin()
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_only(f):
    """Decorator function to ensure user is NOT logged in before
    a page is visited."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_logged_in():
            return redirect(url_for('admin.index'))
        elif 'adminId' in session:
            return redirect(url_for('admin.activate'))
        return f(*args, **kwargs)
    return decorated_function


def unactivated_only(f):
    """Decorator function to ensure user is an admin but not yet activated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'adminId' in session and \
                Admin.query.filter_by(
                    id=session['adminId'],
                    two_factor=False).first() is not None:
            return f(*args, **kwargs)
        return redirect(url_for('admin.index'))
    return decorated_function


def activated_only(f):
    """Decorator function to ensure user is an admin and activated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'adminId' in session and \
                Admin.query.filter_by(
                    id=session['adminId'],
                    two_factor=True).first() is not None:
            return f(*args, **kwargs)
        return redirect(url_for('admin.activate'))
    return decorated_function


def is_logged_in():
    """Is the user logged in?"""
    return 'admin_logged_in' in session and session['admin_logged_in'] is True\
        and 'adminId' in session


def user_exists():
    """Given user is logged in, do they exist in db?"""
    return 'adminId' in session and Admin.query.filter_by(
        id=session['adminId']).first() is not None


def user_activated():
    """Has the user activated 2fa?"""
    return Admin.query.filter_by(
        id=session['adminId'], two_factor=True).first() is not None


def login_admin(username, password):
    """Function to login admin with their username
    Sets:
        - session['adminId'] to the user ID.
    Raises LoginException (represented as e here) if:
        - User with that username does not exist.
        - Password is incorrect.
    """
    admin = Admin.query.filter_by(username=username.lower()).first()
    if admin is not None:
        if not admin.isPassword(password):
            raise LoginException('Password is incorrect.')
        session['adminId'] = admin.id
    else:
        raise LoginException('Username does not exist.')


def login_admin_token(token, force=False):
    admin = Admin.query.filter_by(id=session.get('adminId')).first()
    if not force and not admin.two_factor:
        raise LoginException('Two-factor authentication has not been enabled.')
    if not admin.isToken(token):
        raise LoginException('Token is invalid.')
    session['admin_logged_in'] = True
    session['adminUsername'] = admin.username.lower()


def logout_admin():
    """Log user out."""
    session.pop('admin_logged_in', None)
    session.pop('adminUsername', None)
    session.pop('adminId', None)


class LoginException(Exception):
    pass
