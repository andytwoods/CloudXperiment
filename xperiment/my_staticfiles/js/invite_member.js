$(function () {
    $("#invite_member").bind("click", function (e) {
        $("#input_member").show();
        var width = $("#input_member").find("ul").width();
        $("#input_member").find("input").css("width", width - 2);
        e.preventDefault();
    });

    $("#tag_contact").tagContacts("/scientist/api/contact", {
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
        beforeAdd: function (id) {
            if (is_email(id)) {
                add_member(id);
                return true;
            } else {
                return false;
            }
        },
        beforeRemove: function (id) {
            delete_member(id);
            return true;
        },
        afterRemoved: function (id) {
            console.log("afterRemoved the id: " + id);
        }
    });

    $("#member_list").on("click", "a[name='delete_member']", function (e) {
        if (confirm("Are you sure to delete this member?")) {
            var member_email = $(this).data("member-email");
            delete_member(member_email);
        }
        e.preventDefault();
    });
});

function add_member(member_email) {
    var lab_id = $("#lab_id").val();

    $.ajax({
        url: "/lab/member/add/",
        type: "POST",
        dataType: "json",
        data: {"lab_id": lab_id, "member_email": member_email},
        async: true,
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
        },
        success: function (result) {
            $("#tag_contact").find("li[data-id='" + member_email + "']").remove();
            if (result.status == "success") {
                var obj = {
                    "member_email": result.member_email,
                    "username": result.username,
                    "fullname": result.fullname,
                    "role": result.role,
                    "url": result.url,
                    "created": result.created
                };
                render_member(obj);
            } else {
                console.log(result.message);
            }
        }
    });
}

function delete_member(member_email) {
    var lab_id = $("#lab_id").val();

    $.ajax({
        url: "/lab/member/delete/",
        type: "POST",
        dataType: "json",
        data: {"lab_id": lab_id, "member_email": member_email},
        async: true,
        beforeSend: function (xhr) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
        },
        success: function (result) {
            if (result.status == "success") {
                remove_member(result.member_email);
                $("#tag_contact").find("li[data-id='" + result.member_email + "']").remove();
            } else {
                console.log(result.message);
            }
        }
    });
}

function render_member(obj) {
    var div = _.template($("#tpl_member").html(), obj);
    $("#member_list").append(div);
}

function remove_member(member_email) {
    $("#member_list").find("a[name='delete_member']").each(function () {
        if ($(this).data("member-email") == member_email) {
            $(this).closest("div.row").remove();
        }
    });
}

function is_email(email) {
    var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
    return regex.test(email);
}