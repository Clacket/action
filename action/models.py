import datetime
import os
import base64

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from shapely.geometry import Point
from shapely import wkb
from uuid import uuid4

import geoalchemy2 as ga
import onetimepass

db = SQLAlchemy()

migrate = Migrate()


class Showing(db.Model):
    """The Cinema/Channel table.
    """
    __tablename__ = 'showing'

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    website = db.Column(db.String)
    description = db.Column(db.String)
    phone = db.Column(db.String)
    google_place_id = db.Column(db.String)
    last_modified = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)
    geometry = db.Column(ga.Geography('POINT', srid=4326,
                                      spatial_index=False))
    movies = db.relationship(
        'Movie', secondary='movie_showing',
        back_populates='showings', lazy='dynamic')

    def __init__(self, **kwargs):
        self.type = kwargs.get('type')
        self.name = kwargs.get('name')
        self.phone = kwargs.get('phone')
        self.website = kwargs.get('website')
        self.description = kwargs.get('description')
        self.geometry = kwargs.get('geometry')
        self.google_place_id = kwargs.get('google_place_id')

    @classmethod
    def get_kwargs(self, request):
        geometry = Point(
            float(request.form.get('lng')),
            float(request.form.get('lat')))
        return dict(
            name=request.form.get('name'),
            phone=request.form.get('phone'),
            website=request.form.get('website'),
            description=request.form.get('description'),
            google_place_id=request.form.get('google_place_id'),
            geometry=geometry.wkt)

    @property
    def serialize(self):
        point = wkb.loads(bytes(self.geometry.data))
        lng, lat = point.x, point.y
        return dict(
            name=self.name,
            phone=self.phone,
            website=self.website,
            description=self.description,
            lat=lat,
            lng=lng)


class Movie(db.Model):
    """The Movie table."""

    __tablename__ = 'movie'

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_modified = db.Column(
        db.DateTime, default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)
    showings = db.relationship(
        'Showing', secondary='movie_showing',
        back_populates='movies', lazy='dynamic')

    def __init__(self, **kwargs):
        self.title = kwargs.get('title')
        self.year = kwargs.get('year')
        self.description = kwargs.get('description')

    @property
    def serialize(self):
        return dict(
            id=self.id,
            title=self.title,
            year=self.year,
            description=self.description)

    @classmethod
    def get_kwargs(cls, request):
        return dict(
            title=request.form.get('title'),
            year=request.form.get('year'),
            description=request.form.get('description'))


class MovieShowing(db.Model):
    """Relationship between movie and showing."""

    __tablename__ = 'movie_showing'

    movie_id = db.Column(
        db.BigInteger, db.ForeignKey('movie.id'), primary_key=True)
    showing_id = db.Column(
        db.BigInteger, db.ForeignKey('showing.id'), primary_key=True)
    time_from = db.Column(db.DateTime)
    time_to = db.Column(db.DateTime)


class Admin(db.Model):
    """Table of admins."""

    __tablename__ = 'admin'
    __bind_key__ = 'admin'

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    otp_secret = db.Column(db.String(16), nullable=False)
    two_factor = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, **kwargs):
        self.username = self.check_unique('username', kwargs.get('username'))
        self.email = self.check_unique('email', kwargs.get('email'))
        password_text = self.check_not_none('password', kwargs.get('password'))
        self.password = generate_password_hash(
            password_text, method='pbkdf2:sha512:10000')
        self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    def isPassword(self, text_password):
        return check_password_hash(self.password, text_password)

    def isToken(self, token):
        stripped = [x for x in token if x.isdigit()]
        return len(stripped) > 0 and onetimepass.valid_totp(
            token=int(''.join(stripped)), secret=self.otp_secret)

    @property
    def totp_uri(self):
        return 'otpauth://totp/Clacket:{0}?secret={1}&issuer=Clacket'\
            .format(self.username, self.otp_secret)

    @classmethod
    def check_unique(cls, field, value):
        attribute = getattr(cls, field)
        value = cls.check_not_none(field, value)
        if cls.query.filter(attribute == value).scalar() is not None:
            raise DBException(
                'An admin already exists with {0} = {1}'.format(field, value))
        else:
            return value

    @classmethod
    def check_not_none(cls, field, value):
        if value is not None:
            return value
        else:
            raise DBException(
                'Value for the field: {0} cannot be None.'.format(field))


class AdminInvite(db.Model):
    """Table with admin invitations."""

    __tablename__ = 'invites'
    __bind_key__ = 'admin'

    id = db.Column(db.String(36), primary_key=True)
    created = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    email = db.Column(db.String, unique=True, nullable=False)
    claimed = db.Column(db.DateTime)

    def __init__(self, email):
        self.id = str(uuid4())
        self.email = email


# Utility functions.

def create_geo_index(column):
    """Create geometry index.
    """
    index_name = 'idx_{table}_{column}'.format(
        table=column.table.name,
        column=column.name
    )
    return db.Index(index_name, column, postgresql_using='gist')


# Create geometry indexes:
geo_indexes = []
for table_class in [Showing]:
    column = table_class.__table__.c['geometry']
    geo_indexes.append(create_geo_index(column))


class DBException(Exception):
    pass
