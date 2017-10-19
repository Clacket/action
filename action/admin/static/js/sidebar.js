$('.side-bar .btn').click(function () {
	var selected = $(this);
	var selected_div = $('#' + $(this).data('select'));

	var all = $('.side-bar .btn');
	all.removeClass('selected');
	selected.addClass('selected');

	all.trigger('selectToggle');
});

$('.side-bar .btn').on('selectToggle', function () {
	var btn = $(this);
	var div = $('#' + btn.data('select'));
	if (btn.hasClass('selected')) {
		div.show();
	} else {
		div.hide();
	}
});

$(function () {
	$('.side-bar .btn').first().click();

	var recent_movies = $('#movie-grid');
	$.ajax({
		url: recent_movies.data('href'),
		method: 'GET',
		success: function (data) {
			console.log(data);
		}
	});
});
