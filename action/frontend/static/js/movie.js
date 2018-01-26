$('.hover-icon').hover(function () {
	hover_func(this);
}, function () {
	unhover_func(this);
});

function hover_func(self) {
	if(!$(self).data('unhover')){
		$(self).data('unhover', self.className);
	}
	self.className = $(self).data('hover');
}

function unhover_func(self) {
	self.className = $(self).data('unhover');
}

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

$('.star-action').hover(function () {
	var selector = $(this);
	var parent = selector.parent();
	var i = Number(selector.data('i'));
	var children = $('.star-action', parent);
	children.each(function() {
		if (Number($(this).data('i')) <= i) {
			$(this).removeClass('fa-star-o');
			$(this).addClass('fa-star');
		} else {
			$(this).removeClass('fa-star');
			$(this).addClass('fa-star-o');
		}
	});
});


$('.star-action').click(function () {
	var selector = $(this);
	$('body').css('cursor', 'progress');
	$.ajax({
		url: selector.data('action'),
		method: 'GET',
		success: function (data) {
			$('body').css('cursor', 'default');
			location.reload();
		},
		error: function (e) {
		}
	});
});