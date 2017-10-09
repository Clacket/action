from flask import Flask

from action.models import db, migrate
from action.api import api


def create_app(config_file='config/default.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    app.register_blueprint(api)
    db.init_app(app)
    migrate.init_app(app, db)

    return app


app = create_app()
