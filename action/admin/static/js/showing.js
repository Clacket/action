var cinema_selector = $('#cinema-typeahead .typeahead');
var movie_selector = $('#movie-typeahead .typeahead');

var cinemaList = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  //prefetch: '../data/films/post_1960.json',
  remote: {
    url: cinema_selector.data('endpoint') + '%QUERY',
    wildcard: '%QUERY',
    transform: function (cinemas) { return cinemas.values; }
  }
});
var movieList = new Bloodhound({
  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
  queryTokenizer: Bloodhound.tokenizers.whitespace,
  //prefetch: '../data/films/post_1960.json',
  remote: {
    url: movie_selector.data('endpoint') + '%QUERY',
    wildcard: '%QUERY',
    transform: function (movies) { return movies.values; }
  }
});

cinema_selector.typeahead(null, {
  name: 'chosen-cinema',
  display: 'name',
  source: cinemaList
});
movie_selector.typeahead(null, {
	name: 'chosen-movie',
	display: 'title',
	source: movieList
});

cinema_selector.bind('typeahead:select', function (ev, suggestion) {
	$('#chosen-cinema-id').val(suggestion.id);
});
movie_selector.bind('typeahead:select', function (ev, suggestion) {
	$('#chosen-movie-id').val(suggestion.id);
});
