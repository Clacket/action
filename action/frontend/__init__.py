from flask import Blueprint, render_template

frontend = Blueprint(
    'frontend', __name__, static_folder='static',
    static_url_path='/frontend/static',
    template_folder='templates')


@frontend.route('/')
def index():
    return render_template('frontend_index.html')


@frontend.route('/cinemas')
def cinemas():
    return render_template('frontend_cinemas.html')
