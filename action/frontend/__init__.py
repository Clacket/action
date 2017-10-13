from flask import Blueprint, render_template

frontend = Blueprint(
    'frontend', __name__, static_folder='static',
    template_folder='templates')


@frontend.route('/')
def index():
    return render_template('index.html')
