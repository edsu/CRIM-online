var attachFavouritesAction = function() {
    $('.favorites-link').on({
        'click': function(event) {
            event.preventDefault();
            $.ajax({
                url: $(this).attr('href'),
                context: this,
                success: function(data) {
                    if (data['action'] == 'remove') {
                        $(this).empty();
                        $(this).attr('href', "/favorite/" + data['content'] + "?add");
                        $(this).append('<i class="icon-star-empty"></i> Add to Favourites');
                    } else {
                        $(this).empty();
                        $(this).attr('href', "/favorite/" + data['content'] + "?remove");
                        $(this).append('<i class="icon-star"></i> Remove from Favourites');
                    }
                }
            });
        }
    });
};