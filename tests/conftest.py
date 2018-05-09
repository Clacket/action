import pytest

import action

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
