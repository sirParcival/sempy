$("#add_user_to_group").click(function () {
    let button = $(this).closest("button");
    $.ajax({
        url: button.attr("formaction"),
        data: button.serialize(),
        dataType: 'json',
        success: function (data) {
            if (data.is_ok){
                $("div.my_groups").load(location.href + " div.my_groups")
            }
        }
    });
});

$("#decline_user_request").click(function () {
    let button = $(this).closest("button");
    $.ajax({
        url: button.attr("formaction"),
        data: button.serialize(),
        dataType: 'json',
        success: function (data) {
            if (data.is_ok){
                $("div.my_groups").load(location.href + " div.my_groups")
            }
        }
    });
});