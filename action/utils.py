import os
import boto3
from uuid import uuid4
from urllib.parse import urlparse, urljoin

from flask import redirect, request, url_for, session
from werkzeug.utils import secure_filename
from functools import wraps

from action.models import User

S3_FOLDER = os.environ.get('S3_FOLDER', 'img')
S3_BUCKET = 'clacket'


def redirect_back(endpoint, **values):
    """Helper function to redirect to 'next' URL if it exists.
    Otherwise, redirect to an endpoint."""
    target = request.args.get('next', 0, type=str)
    if not target or not is_safe(target):
        target = url_for(endpoint, **values)
    return redirect(target)


def is_safe(url):
    """Is the URL safe to redirect to?"""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, url))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def str2bool(string):
    if type(string) == bool:
        return string
    return string.lower() == 'true'


def authenticate(f):
    """Decorator function to ensure user is logged in before a page is visited.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in() or not user_exists():
            logout_user()
            return redirect(url_for('frontend.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def anonymous_only(f):
    """Decorator function to ensure user is NOT logged in before
    a page is visited."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if is_logged_in():
            return redirect(url_for('frontend.index'))
        return f(*args, **kwargs)
    return decorated_function


def is_logged_in():
    """Is the user logged in?"""
    return 'userId' in session


def user_exists():
    """Given user is logged in, do they exist in db?"""
    return 'userId' in session and User.query.filter_by(
        id=session['userId']).first() is not None


def login_user(username, password):
    """Function to login user with their username
    Sets:
        - session['userId'] to the user ID.
    Raises LoginException (represented as e here) if:
        - User with that username does not exist.
        - Password is incorrect.
    """
    user = User.query.filter_by(username=username.lower()).first()
    if user is not None:
        if not user.isPassword(password):
            raise LoginException('Password is incorrect.')
        session['userId'] = user.id
        session['userUsername'] = user.username.lower()
    else:
        raise LoginException('Username does not exist.')


def logout_user():
    """Log user out."""
    session.pop('userId', None)
    session.pop('userUsername', None)


def upload_picture(file):
    if file.content_type[:6] == 'image/':
        source_filename = secure_filename(file.filename)
        destination_filename = '{0}/{1}_{2}'.format(
            S3_FOLDER, uuid4().hex, source_filename)
        file.filename = destination_filename
        return upload_to_s3(file)
    else:
        raise UploadException('File is not an image.')


def s3_url(filename):
    return 'https://{0}.s3.amazonaws.com/{1}'.format(
        S3_BUCKET, filename)


def upload_to_s3(file, acl='public-read'):
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            file.filename,
            ExtraArgs={
                'ACL': acl,
                'ContentType': file.content_type
            }
        )
        return s3_url(file.filename)
    except Exception as e:
        print(str(e))
        raise UploadException('Could not upload photo. Please try again.')


class UploadException(Exception):
    pass


class LoginException(Exception):
    pass
