import datetime
import os
import base64

from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

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
    geometry = db.Column(ga.Geography('POLYGON', srid=4326,
                                      spatial_index=False))
    movies = db.relationship(
        'Movie', secondary='movie_showing',
        back_populates='showings', lazy='dynamic')


class Movie(db.Model):
    """The Movie table."""

    __tablename__ = 'movie'

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    showings = db.relationship(
        'Showing', secondary='movie_showing',
        back_populates='movies', lazy='dynamic')


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
        return onetimepass.valid_totp(token=token, secret=self.otp_secret)

    @property
    def totp_uri(self):
        return 'otpauth://totp/Clacket:{0}?secret={1}&issuer=Clacket'\
            .format(self.username, self.otp_secret)

    @classmethod
    def check_unique(cls, field, value):
        attribute = getattr(cls, field)
        value = cls.check_not_none(value)
        if cls.query(attribute == value).scalar() is not None:
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
    email = db.Column(db.String, nullable=False)
    claimed = db.Column(db.DateTime)


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
