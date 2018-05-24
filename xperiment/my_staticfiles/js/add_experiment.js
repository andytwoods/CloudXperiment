$(function () {
    var cells = $('.table').find('tr')[0].cells.length;
    var desired_width = $('.table').width() / cells + "px";
    $('.table td').css('width', desired_width);

    $("#sortable").sortable({
        axis: "y",
        stop: function (e, ui) {
            console.log(ui.item.children('td'));
            ui.item.children('td').effect('highlight', {}, 1000);
        },
        update: function (e, ui) {
            var item_id = ui.item.data('item_id');
            var position = ui.item.index() + 1;
            $.ajax({
                url: "/lab/course/experiment/changeorder/",
                type: "POST",
                dataType: "json",
                data: {item_id: item_id, order: position},
                async: true,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                }
            });
        }
    });
    $("#sortable").disableSelection();

    var api_url = "/lab/course/" + course_id + "/api/experiment/";
    init_experiments_input(api_url);

    $("body").on("click", "a.course_expt_delete", function (e) {
        var a = $(this);
        var item_id = a.data('item_id');
        $.ajax({
            url: "/lab/course/experiment/delete/",
            type: "POST",
            dataType: "json",
            data: {item_id: item_id},
            async: true,
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
            },
            success: function (data) {
                if (data.status == "success") {
                    a.closest("tr").remove();
                }
            }
        });
    });

    $("#add_experiment").on("click", function (e) {
        if (experiment_list.length > 0) {
            $.ajax({
                url: "/lab/course/experiment/add/",
                type: "POST",
                dataType: "json",
                data: {course_id: course_id, experiment_list: experiment_list},
                async: true,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                },
                success: function (result) {
                    if (result.status == "success") {
                        $.each(result.experiments, function (i, experiment) {
                            render_experiment(experiment);
                        });
                        init_experiments_input(api_url);
                        experiment_list = [];
                    } else {
                        console.log(result.message);
                    }
                }
            });
        }
    });
});

function render_experiment(experiment) {
    var tr = _.template($("#tpl_experiment").html(), experiment);
    $("#sortable").append(tr);
}

function is_email(email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
}

function init_experiments_input(api_url) {
    $("#select_experiment").empty();
    $("#select_experiment").tagContacts(api_url, {
        // Min input width, default is 60
        minInputWidth: 60,
        // Min dropdown width, default is 300
        minDropdownWidth: 300,
        // Max items in the dropdown list, default is 5
        maxItemNumber: 5,
        // Min length to trigger the dropdown list, default is 1
        minLength: 1,
        // Can provide an exists contacts list here, default is null
        selectedContacts: [],
        beforeAdd: function (expt_id) {
            experiment_list.push(expt_id)
        },
        beforeRemove: function (expt_id) {
            return true;
        },
        afterRemoved: function (expt_id) {
            experiment_list.remove(expt_id);
        }
    });
}

Array.prototype.remove = function () {
    var what, a = arguments, L = a.length, ax;
    while (L && this.length) {
        what = a[--L];
        while ((ax = this.indexOf(what)) !== -1) {
            this.splice(ax, 1);
        }
    }
    return this;
};