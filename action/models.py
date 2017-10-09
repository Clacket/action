from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import geoalchemy2 as ga

db = SQLAlchemy()

migrate = Migrate()


class Cinema(db.Model):
    """The Cell table.
    """
    __tablename__ = 'cinema'

    id = db.Column(db.BigInteger, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    website = db.Column(db.String)
    description = db.Column(db.String)
    phone = db.Column(db.String)
    geometry = db.Column(ga.Geography('POLYGON', srid=4326,
                                      spatial_index=False))


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
for table_class in [Cinema]:
    column = table_class.__table__.c['geometry']
    geo_indexes.append(create_geo_index(column))
