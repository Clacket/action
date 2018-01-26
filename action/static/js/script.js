$('.alert').alert();
$('.clickable').click(function () {
	window.location.href = $(this).data('href');
});
$('.recent-grid').each(function () {
	var selector = $(this);
	$.ajax({
		url: selector.data('href'),
		method: 'GET',
		success: function (data) {
			selector.html(data);
		}
	});
});
