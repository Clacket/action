$('.side-bar .btn').click(function () {
	var selected_btn = $(this);
	var selected_div = $('#' + $(this).data('select'));
	var all_btns = $('.side-bar .btn');
	var all_divs = $('.content-bar .content');
	all_btns.removeClass('selected');
	all_divs.hide();
	selected_btn.addClass('selected');
	selected_div.show();
});
