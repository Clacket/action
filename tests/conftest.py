import os

from dotenv import load_dotenv

import pytest

import action


@pytest.fixture(scope='session', autouse=True)
def dotenv():
    """Load dotenv file."""
    load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))


@pytest.fixture
def app():
    """Get the flask app."""
    # Set database to test database.
    app = action.create_app(config_file='config/testing.py')
    return app


@pytest.fixture
def db(app):
    """Get the flask db."""
    with action.db.engine.connect() as conn:
        trans = conn.begin()
        yield action.db
        trans.rollback()
