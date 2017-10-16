from flask import redirect, url_for, request, session
from functools import wraps

from action.models import Admin


def authenticate(f):
    """Decorator function to ensure user is logged in before a page is visited.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in() or not user_exists():
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
        return f(*args, **kwargs)
    return decorated_function


def is_logged_in():
    """Is the user logged in?"""
    return 'admin_logged_in' in session and session['admin_logged_in'] is True\
        and 'adminId' in session


def user_exists():
    """Given user is logged in, do they exist in db?"""
    return Admin.query.filter_by(id=session['adminId']).first() is not None


def login_admin(username, password, token=None):
    """Function to login admin with their username
    Sets:
        - session['admin_logged_in'] to True.
        - session['adminUsername'] to the username.
        - session['adminId'] to the user ID.
    Raises LoginException (represented as e here) if:
        - User with that username does not exist.
        - Password is incorrect.
        - Token is invalid.
    """
    admin = Admin.query.filter_by(username=username.lower()).first()
    if admin is not None:
        if not admin.isPassword(password):
            raise LoginException('Password is incorrect.')
        if token is not None and not admin.isToken(token):
            raise LoginException('Token is invalid.')
        session['admin_logged_in'] = True
        session['adminUsername'] = username.lower()
        session['adminId'] = admin.id
    else:
        raise LoginException('Username does not exist.')


def logout_admin():
    """Log user out."""
    session.pop('admin_logged_in', None)
    session.pop('adminUsername', None)
    session.pop('adminId', None)


class LoginException(Exception):
    pass
