from flask_migrate import upgrade

from action import create_app


def update_db():
    app = create_app(config_file='config/testing.py')
    with app.app_context():
        upgrade()


if __name__ == '__main__':
    update_db()
