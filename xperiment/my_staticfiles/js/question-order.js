$(document).ready(function () {
    $("#btn_add_order").on("click", function () {
        var order_text = $("#order_text").val();
        var reg = /^(\d+,?)+$/;
        if (order_text && reg.test(order_text)) {
            order_text = order_text.replace(/,$/gi, "");
            var obj = {
                "sequence": "#",
                "order": order_text
            };
            $("#order_text").val("");
            var tr = _.template($("#tpl_order_table").html(), obj);
            $("#order_table").find("tbody").append(tr);
            refresh_sequence();
        }
    });

    $("#order_table").on("click", "a[name='btn_remove_order']", function () {
        $(this).parents("tr").remove();
        refresh_sequence();
    });

    $("#create_experiment_form, #edit_experiment_form").submit(function () {
        var $this = $(this);
        $.each(get_order_list(), function (i, item) {
            $this.append(_.template($("#tpl_order_form").html(), {"order": item}));
        });
    });
});

function refresh_sequence() {
    $("#order_table").find("tbody tr").each(function (i, item) {
        $(item).find("td:first").text(i + 1);
    });
}

function get_order_list() {
    var order_list = [];
    $("#order_table").find("tbody tr").each(function (i, item) {
        var $td = $(item).find("td:eq(1)");
        if (!$td.attr("data-id")) {
            order_list.push($td.text());
        }
    });
    return order_list;
}