
$("button.handle_request").click(function (event) {
    event.preventDefault();
    let button = $(this).closest("button");
    let li = $(this).closest("li");
    $.ajax({
        url: button.attr("formaction"),
        type: 'GET',
        success: function (data) {
            $(li).fadeOut(100, null)
        }
    });
});

$("button.group_handler").click(function (event) {
    event.preventDefault();
    const button = $(this).closest("button");
    const li = $(this).closest("li");
    const a = li.children('a');
    const form = $(this).closest('form');
    $.ajax({
        url: button.attr("formaction"),
        data: form.serialize(),
        dataType: 'json',
        type: 'GET',
        success: function (data) {
            if (data.is_rename){
                $(a).fadeOut(100, function () {
                    $(a).text(data.text).fadeIn();
                });

            }
            else {
                $(li).fadeOut(100, null);
            }
        }
    });
});