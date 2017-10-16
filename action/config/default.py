import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
SQLALCHEMY_BINDS = {
    'admin': os.environ.get('ADMIN_DATABASE_URL')
}
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
    'SQLALCHEMY_TRACK_MODIFICATIONS', False)
DEBUG = os.environ.get('DEBUG', False)
SECRET_KEY = os.environ.get('SECRET_KEY')
SERVER_NAME = os.environ.get('SERVER_NAME')
PREFERRED_URL_SCHEME = 'https'
