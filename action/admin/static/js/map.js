var new_cinema = document.getElementById('newCinema');
autocomplete = new google.maps.places.Autocomplete(new_cinema);
autocomplete.addListener('place_changed', function () {
	var place = autocomplete.getPlace();

	var prefix = '#newCinema';
	var lat_el = $(prefix + 'lat');
	var lng_el = $(prefix + 'lng');
	var place_id_el = $(prefix + 'google_place_id');

	if (!place.geometry) {
		$(prefix).val('');
	}
	lat_el.val(place.geometry.location.lat());
	lng_el.val(place.geometry.location.lng());
	place_id_el.val(place.place_id);
});