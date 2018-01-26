mapboxgl.accessToken = 'pk.eyJ1IjoibWFhcm91ZiIsImEiOiJjajkxbnJuaXoyaXgwMnFyMDViZmNkaWc1In0.IXP3SdK0YZ9j7D0l6UDzsg';

var map = new mapboxgl.Map({
	container: 'map',
	style: 'mapbox://styles/maarouf/cj8q5lwfu31322rn6mzira92l',
	center: [29.9187, 31.2001],
	zoom: 12
});

// Add zoom and rotation controls to the map.
map.addControl(new mapboxgl.NavigationControl());

var user_marker = new mapboxgl.Marker();

function init() {	
	navigator.geolocation.getCurrentPosition(function(pos) {
		var value = $('#radius-box').val();
		getCinemas(pos, value, function (cinemas) {
			var center = [ pos.coords.longitude, pos.coords.latitude ];
			map.setCenter(center);
			map.addSource("polygon", createGeoJSONCircle(center, 5));
			map.addLayer({
				"id": "polygon",
				"type": "fill",
				"source": "polygon",
				"layout": {},
				"paint": {
				    "fill-color": "rgb(52, 152, 219)",
				    "fill-opacity": 0.4
				}
			});
			var data = getPositionGeo(pos);
			map.addSource("user_position", data);
			map.addLayer({
				"id": "user_position",
				"type": "symbol",
				"source": "user_position",
				"layout": {
				    "icon-image": "{icon}-15",
				    "text-field": "{title}",
				    "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
				    "text-offset": [0, 0.6],
				    "text-anchor": "top"
				}
			});

			var cinema_data = getCinemaGeo(cinemas);
			map.addSource("cinemas", cinema_data)
			map.addLayer({
				"id": "cinemas",
				"type": "symbol",
				"source": "cinemas",
				"layout": {
				    "icon-image": "{icon}-15",
				    "text-field": "{title}",
				    "text-font": ["Open Sans Semibold", "Arial Unicode MS Bold"],
				    "text-offset": [0, 0.6],
				    "text-anchor": "top",
				    "icon-allow-overlap": true
				}
			});

			// When a click event occurs on a feature in the places layer, open a popup at the
		    // location of the feature, with description HTML from its properties.
		    map.on('click', 'cinemas', function (e) {
		        new mapboxgl.Popup()
		            .setLngLat(e.features[0].geometry.coordinates)
		            .setHTML(e.features[0].properties.description)
		            .addTo(map);
		    });

		    // Change the cursor to a pointer when the mouse is over the places layer.
		    map.on('mouseenter', 'cinemas', function () {
		        map.getCanvas().style.cursor = 'pointer';
		    });

		    // Change it back to a pointer when it leaves.
		    map.on('mouseleave', 'cinemas', function () {
		        map.getCanvas().style.cursor = '';
		    });
		});
	});
}

map.on("load", init);


// src: https://stackoverflow.com/a/39006388
var createGeoJSONCircle = function(center, radiusInKm, points) {
    if(!points) points = 64;

    var coords = {
        latitude: center[1],
        longitude: center[0]
    };

    var km = radiusInKm;

    var ret = [];
    var distanceX = km/(111.320*Math.cos(coords.latitude*Math.PI/180));
    var distanceY = km/110.574;

    var theta, x, y;
    for(var i=0; i<points; i++) {
        theta = (i/points)*(2*Math.PI);
        x = distanceX*Math.cos(theta);
        y = distanceY*Math.sin(theta);

        ret.push([coords.longitude+x, coords.latitude+y]);
    }
    ret.push(ret[0]);

    return {
        "type": "geojson",
        "data": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [ret]
                }
            }]
        }
    };
};

function refresh () {
	navigator.geolocation.getCurrentPosition(function(pos) {
		var value = $('#radius-box').val();
		getCinemas(pos, value, function (cinemas) {
			var center = [ pos.coords.longitude, pos.coords.latitude ];
			map.setCenter(center);
			map.getSource("polygon").setData(createGeoJSONCircle(center, value));
			map.getSource("user_position").setData(getPositionGeo(pos));
			map.getSouce("cinemas").setData(getCinemaGeo(cinemas));
		});
	});
}

function getPositionGeo(pos) {
	var center = [ pos.coords.longitude, pos.coords.latitude ];
	return {
			"type": "geojson",
			"data": {
			   "type": "FeatureCollection",
			   "features": [{
			       "type": "Feature",
			       "properties": {
			      	  "title": "You are here",
			      	  "icon": "circle"
			        },
			       "geometry": {
			          "type": "Point",
			          "coordinates": center
			      	}
			  	}]
			}
		}
}

function getCinemaGeo(cinemas) {
	return {
		"type": "geojson",
		"data": {
			"type": "FeatureCollection",
			"features": cinemas
		}
	}
}

var getCinemas = function (pos, radiusInKm, callback) {
	$.ajax({
		method: 'GET',
		url: $('#map').data('endpoint'),
		data: {
			lng: pos.coords.longitude,
			lat: pos.coords.latitude,
			radius: radiusInKm
		},
		type: 'json',
		success: function (json) {
			var cinemas = [];
			for (var i = 0; i < json.cinemas.length; i++) {
				cinemas.push({
				    "type": "Feature",
				    "properties": {
				   	  "title": json.cinemas[i].name,
				   	  "icon": "star",
				   	  "description": "<strong>" + json.cinemas[i].name + "</strong><br>" + json.cinemas[i].description + "<br>" + json.cinemas[i].phone
				     },
				    "geometry": {
				       "type": "Point",
				       "coordinates": [json.cinemas[i].lng, json.cinemas[i].lat]
				    }
				});
			}
			callback(cinemas);
		}
	});
}

$('#radius-box').change(refresh);
