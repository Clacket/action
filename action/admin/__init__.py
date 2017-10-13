from flask import Blueprint

admin = Blueprint('admin', __name__, subdomain='admin')


@admin.route('/')
def index():
    return 'Hi, Admin'
