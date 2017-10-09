import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../../.env'))

SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get(
    'SQLALCHEMY_TRACK_MODIFICATIONS', False)
DEBUG = os.environ.get('DEBUG', True)
TESTING = True
SECRET_KEY = os.environ.get('SECRET_KEY')
