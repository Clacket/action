from flask import Blueprint, jsonify, request
from sqlalchemy import and_
from shapely.geometry import Point

from action.models import Showing, MovieShowing
# from action.utils import (
#     authenticate, anonymous_only)

api = Blueprint('api', __name__, url_prefix='/api/v1')


@api.route('/cinemas/nearby')
def nearby_cinemas():
    lat, lng = float(request.args.get('lat')), float(request.args.get('lng'))
    location = 'SRID=4326;{0}'.format(Point(lng, lat).wkt)
    radius_meters = float(request.args.get('radius')) * 1000
    cinemas = Showing.query.filter(
        and_(
            Showing.type == 'cinema',
            Showing.geometry.ST_Distance(location) <= radius_meters
        )).all()
    cinemas_list = [x.serialize for x in cinemas]
    return jsonify(cinemas=cinemas_list)


@api.route('/movie/<int:movie_id>/showings/nearby')
def nearby_showings(movie_id):
    lat, lng = float(request.args.get('lat')), float(request.args.get('lng'))
    location = 'SRID=4326;{0}'.format(Point(lng, lat).wkt)
    radius_meters = float(request.args.get('radius')) * 1000
    cinemas = Showing.query.join(MovieShowing).filter(
        and_(
            MovieShowing.movie_id == movie_id,
            Showing.type == 'cinema',
            Showing.geometry.ST_Distance(location) <= radius_meters
        )).all()
    cinemas_list = [x.serialize for x in cinemas]
    return jsonify(cinemas=cinemas_list)
