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


@frontend.route('/.well-known/acme-challenge/'
                'Hi2hDN1w5no0sG0L6cOZ97s-x-kaighlHymxX_N8mkk')
def challenge():
    return 'Hi2hDN1w5no0sG0L6cOZ97s-x-kaighlHymxX_N8mkk.1dYUIFasTS8DhTLxaz2'\
            'kpn47w20_TLA32KNVvEWSbLY'
