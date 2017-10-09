from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

import geoalchemy2 as ga

db = SQLAlchemy()

migrate = Migrate()


# 1. Entities

class Cell(db.Model):
    """The Cell table.
    """
    __tablename__ = 'cell'

    cell_id = db.Column(db.BigInteger, autoincrement=True, primary_key=True)
    region = db.Column(db.String, nullable=False)
    cell_name = db.Column(db.String, nullable=False)
    geometry = db.Column(ga.Geography('POLYGON', srid=4326,
                                      spatial_index=False))

    def __init__(self, region='test', cell_name=None):
        self.region = region
        self.cell_name = cell_name if cell_name is not None else 'test-cell'


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
for table_class in [Cell]:
    column = table_class.__table__.c['geometry']
    geo_indexes.append(create_geo_index(column))
