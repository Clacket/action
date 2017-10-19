$('.alert').alert();
$('.clickable').click(function () {
	window.location.href = $(this).data('href');
});