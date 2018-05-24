$(function () {
    var api_url = "/lab/course/" + course_id + "/api/user/";
    init_participants_input(api_url);

    $("body").on("click", "a.course_participant_delete", function (e) {
        var a = $(this);
        var item_id = a.data('item_id');
        $.ajax({
            url: "/lab/course/participant/delete/",
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

    $("#add_participant").on("click", function(e){
        if (email_list.length > 0) {
            var ed = tinyMCE.get('id_notification_message');
            var custom_content = ed.getContent();

            $.ajax({
                url: "/lab/course/participant/add/",
                type: "POST",
                dataType: "json",
                data: {course_id: course_id, email_list: email_list, custom_content: custom_content},
                async: true,
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                },
                success: function (result) {
                    if (result.status == "success") {
                        $.each(result.participants, function(i, participant){
                            render_participant(participant);
                        });
                        init_participants_input(api_url);
                        email_list = [];
                    } else {
                        console.log(result.message);
                    }
                }
            });
        }
    });
});

function render_participant(participant) {
    var tr = _.template($("#tpl_participant").html(), participant);
    $("#course_participants").append(tr);
}

function is_email(email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
}

function init_participants_input(api_url) {
    $("#select_participant").empty();
    $("#select_participant").tagContacts(api_url, {
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
        beforeAdd: function (email) {
            if (is_email(email)) {
                email_list.push(email);
                return true;
            } else {
                return false;
            }
        },
        beforeRemove: function (email) {
            return true;
        },
        afterRemoved: function (email) {
            email_list.remove(email);
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