from flask import Flask, _request_ctx_stack

from action.models import db, migrate
from action.extensions import mail
from action.api import api
from action.frontend import frontend
from action.admin import admin


def create_app(config_file='config/default.py'):
    app = Flask(__name__)
    app.config.from_pyfile(config_file)
    app.register_blueprint(api)
    app.register_blueprint(frontend)
    app.register_blueprint(admin)
    db.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)

    return app


app = create_app()


def force_https():
    if not app.debug:
        if _request_ctx_stack is not None:
            reqctx = _request_ctx_stack.top
            reqctx.url_adapter.url_scheme = 'https'


app.before_request(force_https)
