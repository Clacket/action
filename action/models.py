from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import geoalchemy2 as ga

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
