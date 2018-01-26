$('.hover-icon').hover(function () {
	if(!$(this).data('unhover')){
		$(this).data('unhover', this.className);
	}
	this.className = $(this).data('hover');
}, function () {
	this.className = $(this).data('unhover');
});

$('.action').click(function () {
	var selector = $(this);
	var unhover = selector.data('unhover');
	selector.data('unhover', selector.data('hover'));
	$('body').css('cursor', 'progress');
	$.ajax({
		url: selector.data('action'),
		method: 'GET',
		success: function (data) {
			$('body').css('cursor', 'default');
		},
		error: function (e) {
			selector.data('unhover', unhover);
		}
	});
});