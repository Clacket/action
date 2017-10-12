from flask import Blueprint, render_template

frontend = Blueprint(
    'frontend', __name__, static_folder='static',
    template_folder='templates')


@frontend.route('/')
def index():
    return render_template('index.html')


@frontend.route('/.well-known/acme-challenge/'
                'rK9944ZpatukKmgBTg_qWamQ2zP23NaWHFDygo8_r5g')
def challenge():
    return 'rK9944ZpatukKmgBTg_qWamQ2zP23NaWHFDygo8_r5g.'\
            '1dYUIFasTS8DhTLxaz2kpn47w20_TLA32KNVvEWSbLY'
