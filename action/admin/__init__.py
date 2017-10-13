from flask import Blueprint

admin = Blueprint('admin', __name__, subdomain='admin')


@admin.route('/')
def index():
    return 'Hi, Admin'


@admin.route('/.well-known/acme-challenge/'
             '_nL7FhKCWZDsOVKjOLBu3aRaxYm-ceYhSzNN9f1PBNY')
def challenge():
    return '_nL7FhKCWZDsOVKjOLBu3aRaxYm-ceYhSzNN9f1PBNY.'\
           '1dYUIFasTS8DhTLxaz2kpn47w20_TLA32KNVvEWSbLY'
