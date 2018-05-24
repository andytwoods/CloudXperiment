$(function () {
    String.prototype.trimToLength = function (m, cut_word) {
        if (cut_word) {
            return (this.length > m)
                ? jQuery.trim(this).substring(0, m).split(" ").slice(0, -1).join(" ") + "..."
                : this;
        } else {
            return (this.length > m)
                ? jQuery.trim(this).substring(0, m) + "..."
                : this;
        }
    };

    $("#modal_signin_form, #signup_form").submit(function () {
        var form = $(this);
        $.ajax({
            url: "/accounts/login/",
            data: form.serialize(),
            dataType: "json",
            type: "POST",
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
            },
            success: function (data) {
                //console.log(data);
                $("div.form_errors").html("");
                $("div.form_errors").hide();
                window.location.href = data.location;
            },
            error: function (xhr, status, error) {
                //console.log(xhr.responseText);
                var error = JSON.parse(xhr.responseText);
                if (error.form_errors.__all__) {
                    $("div.signin_errors").html("");
                    $.each(error.form_errors.__all__, function (i, error_msg) {
                        $("div.signin_errors").append("<p>" + error_msg + "</p>");
                    });
                    $("div.signin_errors").show();
                }

                if (error.form_errors.login) {
                    $("input[name=login]").parent().addClass("has-error");
                }

                if (error.form_errors.password) {
                    $("input[name=password]").parent().addClass("has-error");
                }
            }
        });
        return false;
    });

    $("#modal_signup_form, #signup_form").submit(function () {
        var form = $(this);
        $.ajax({
            url: "/signup/ajax/",
            data: form.serialize(),
            dataType: "json",
            type: "POST",
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
            },
            success: function (data) {
                //console.log(data);
                $("#modal_signup_form input").parent().removeClass("has-error");
                if (data.status == "success") {
                    $("div.signup_errors").hide();
                    $("div.signup_errors").html("");
                    window.location.href = data.next;
                } else {
                    $("div.signup_errors").html("");
                    $.each(data.error, function (key, value) {
                        $("div.signup_errors").append("<p>" + value + "</p>");
                        $("#modal_signup_form input[name=" + key + "]").parent().addClass("has-error");
                    });
                    $("div.signup_errors").show();

                }
            },
            error: function (xhr, status, error) {
                console.log(xhr.responseText);
            }
        });
        return false;
    });

    $("a.modal_signup_link").click(function (e) {
        e.preventDefault();
        $("#signin_modal").modal("hide");
        $("#signup_modal").modal("show");
    });

    $("a.modal_signin_link").click(function (e) {
        e.preventDefault();
        $("#signup_modal").modal("hide");
        $("#signin_modal").modal("show");
    });

    $("#error_list li").each(function () {
        var fid = $(this).attr("data-field-id");
        var error = $(this).html();
        $("#" + fid).closest("div.form-group").addClass("has-error");
        $("#" + fid).parent().append("<p class='help-block'>" + error + "</p>");
    });

    $("a[name='btn_mturk_submit']").on("click", function (e) {
        var $parent = $(this);
        var expt_id = $(this).data("expt-id");

        $.colorbox({
            html: $("#mturk_confirm_modal").html(),
            width: 800,
            opacity: 0.8,
            overlayClose: false,
            closeButton: true,
            title: function () {
                return "<img src='/static/img/logo.png' style='width:100px;'>"
            },
            onComplete: function () {
                $("a[name='btn_mturk_confirm']").on("click", function (e) {
                    var access_key = $(this).data("access-key");
                    var url = "/mturk/" + expt_id + "/" + access_key + "/edit/";

                    if (access_key) {
                        create_mturk_question_modal(url);
                    } else {
                        $("#mturk_no_confirm_modal").modal().one('click', '#submit_confirm', function () {
                            create_mturk_question_modal(url);
                        });
                    }
                    e.preventDefault();
                });

                $("a[name='btn_mturk_password']").on("click", function (e) {
                    var $this = $(this);
                    var $input = $this.parents(".input-group").find("input:first");
                    var $next = $this.next();
                    var assignment_id = $input.val();

                    if (assignment_id) {
                        $.ajax({
                            url: "/api/mturk/password/get/",
                            data: {"assignment_id": assignment_id},
                            dataType: "json",
                            type: "GET",
                            beforeSend: function (xhr) {
                                $this.attr("disabled", "disabled");
                            },
                            success: function (result) {
                                if (result.status == "success") {
                                    $this.popover("destroy");

                                    $this.popover({
                                        title: "Password",
                                        placement: "top",
                                        html: true,
                                        content: '<div class="text-center"><b>' + result.password + '</b></div>'
                                    });

                                    $this.popover("show");
                                } else {
                                    new PNotify({
                                        title: "Mechanical Turk",
                                        text: result.message,
                                        type: result.status
                                    });
                                }
                            },
                            error: function (xhr, status, error) {
                                console.log(xhr.responseText);
                            },
                            complete: function () {
                                $this.removeAttr("disabled");
                            }
                        });
                    } else {
                        $input.focus();
                        new PNotify({
                            title: "Message",
                            text: "Please enter assignment id to get the password",
                            type: "info"
                        });
                    }

                    e.preventDefault();
                });
            }
        });

        e.preventDefault();
    });

    $("a[name='btn_mturk_confirm_admin']").on("click", function (e) {
        var access_key = $(this).data("access-key");
        var mt_id = $(this).data("mt-id");
        var expt_id = $(this).data("expt-id");
        var url = "/mturk/" + expt_id + "/" + access_key + "/edit/?mt_id=" + mt_id;
        create_mturk_question_modal(url);
        e.preventDefault();
    });


    $("a[name='btn_change_order']").on("click", function (e) {
        var $parent = $(this);
        var expt_id = $(this).data("expt-id");

        $.colorbox({
            href: "/experiment/" + expt_id + "/change/order/",
            fastIframe: false,
            overlayClose: false,
            closeButton: true,
            opacity: 0.7,
            width: 750,
            height: "80%",
            title: function () {
                return "<img src='/static/img/logo.png' style='width:100px;'>"
            },
            onComplete: function () {
                function _get_select_order_count() {
                    var count = 0;
                    $("input[name='ck_order']").each(function () {
                        if ($(this).is(":checked")) {
                            count++;
                        }
                    });
                    return count;
                }

                function _get_select_order_ids() {
                    var ids = [];
                    $("input[name='ck_order']").each(function () {
                        if ($(this).is(":checked")) {
                            ids.push($(this).val());
                        }
                    });
                    return ids;
                }

                function _remove_select_order_row(id) {
                    $("body").find("input[name='ck_order']").each(function () {
                        if (id) {
                            if ($(this).val() == id) {
                                $(this).closest("tr").remove();
                            }
                        } else {
                            if ($(this).is(":checked")) {
                                $(this).closest("tr").remove();
                            }
                        }
                    });
                }

                function _ajax_delete_order(target, order_ids) {
                    $.ajax({
                        url: "/experiment/" + expt_id + "/order/delete/",
                        data: {"order_ids": order_ids},
                        dataType: "json",
                        type: "POST",
                        beforeSend: function (xhr) {
                            $(target).prop("disabled", true);
                            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                        },
                        success: function (result) {
                            if (result.status == "success") {
                                if (order_ids.length == 1) {
                                    _remove_select_order_row(order_ids[0]);
                                } else {
                                    _remove_select_order_row();
                                }
                            } else {
                                new PNotify({
                                    title: "Change Order",
                                    text: result.message,
                                    type: "error"
                                });
                            }
                        },
                        error: function (xhr, status, error) {
                            console.log(xhr.responseText);
                        },
                        complete: function () {
                            $(target).prop("disabled", false);
                        }
                    });
                }

                function _refresh_sequence() {
                    $("#order_table").find("tbody tr").each(function (i, item) {
                        $(item).find("td:eq(1)").text(i + 1);
                    });
                }

                $("#select_all_order").on("click", function (e) {
                    var checked = $(this).prop("checked")();
                    $("input[name='ck_order']").each(function () {
                        if (!$(this).prop("disabled")) {
                            $(this).prop("checked", checked);
                        }
                    });
                    e.preventDefault();
                });

                $("body").on("click", "a[name='btn_remove_order']", function (e) {
                    var $this = $(this);
                    if (confirm("Can you sure want to delete the order? Refresh page to see changes.")) {
                        _ajax_delete_order($this, [$this.data("order-id")]);
                    }
                    e.preventDefault();
                });

                $("#btn_remove_order_all").on("click", function (e) {
                    var $this = $(this);
                    if (_get_select_order_count() <= 0) {
                        new PNotify({
                            title: "Change Order",
                            text: "Please select at least one",
                            type: "info"
                        });
                        return false;
                    } else if (confirm("Are you sure want to delete selected order?")) {
                        _ajax_delete_order($this, _get_select_order_ids());
                    }
                    e.preventDefault();
                });



                $("#btn_modify_counts").on("click", function (e) {

                    if (confirm("Are you sure want to modify the orders?")) {
                        var target = $(this);
                        $.ajax({
                        url: "/experiment/" + expt_id + "/order/batch/modify_order/",
                        data: {'modify_order[]':get_order_info()},
                        dataType: "json",
                        type: "POST",
                        beforeSend: function (xhr) {
                            $(target).prop("disabled", true);
                            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                        },
                        success: function (result) {

                        },
                        error: function (xhr, status, error) {
                            console.log(xhr.responseText);
                        },
                        complete: function () {
                            $(target).prop("disabled", false);
                        }
                    });



                    }
                    e.preventDefault();

                    function get_order_info(){
                        var arr = [];
                        var obj;

                        $('#order_table > tbody > tr').each(function() {
                            var $td =  $('td', this);
                            obj = {count: $td.find("#new_count").val(), cond:  $($td.eq(3)).text() };
                            arr.push(obj);
                        });

                        return JSON.stringify(arr);
                    }

                });


                $("#btn_batch_add_order_toggle").on("click", function (e) {
                    $("#batch_add_order_content").toggleClass("hide");
                    e.preventDefault();
                });

                $("#btn_batch_add_order").on("click", function (e) {
                    var batch_order_text = $("#batch_order_text").val();

                    if (batch_order_text) {
                        var is_validate = false;
                        var batch_order_text_list = batch_order_text.split("\n");

                        $(batch_order_text_list).each(function (index, item) {
                            if (item) {
                                batch_order_text_list[index] = item.replace(/,$/gi, "");
                                is_validate = true;
                            }
                        });

                        if (is_validate) {
                            batch_order_text = batch_order_text_list.join("\n");

                            $.ajax({
                                url: "/experiment/" + expt_id + "/order/batch/add/",
                                data: {"batch_order": batch_order_text},
                                dataType: "json",
                                type: "POST",
                                beforeSend: function (xhr) {
                                    $(this).prop("disabled", true);
                                    xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                                },
                                success: function (result) {
                                    if (result.status == "success") {
                                        $.each(result.objects, function (i, item) {
                                            if (item.created) {
                                                var obj = {
                                                    "id": item.id,
                                                    "sequence": "#",
                                                    "order": item.order
                                                };
                                                var tr = _.template($("#tpl_order_row").html(), obj);
                                                $("#order_table").find("tbody").append(tr);
                                            } else {
                                                new PNotify({
                                                    title: "Change Order",
                                                    text: "The order [" + item.order + "] already exists",
                                                    type: "info"
                                                });
                                            }
                                        });
                                        $("#batch_order_text").val("");
                                        _refresh_sequence();
                                    } else {
                                        new PNotify({
                                            title: "Change Order",
                                            text: result.message,
                                            type: "error"
                                        });
                                    }
                                },
                                error: function (xhr, status, error) {
                                    console.log(xhr.responseText);
                                },
                                complete: function () {
                                    $(this).prop("disabled", false);
                                }
                            });
                        } else {
                            new PNotify({
                                title: "Change Order",
                                text: "Please enter the correct text",
                                type: "info"
                            });
                        }
                    } else {
                        new PNotify({
                            title: "Change Order",
                            text: "Please enter the correct text",
                            type: "info"
                        });
                    }
                    e.preventDefault();
                });
            },
            onClosed: function () {
                $("body").unbind("click a[name='btn_remove_order']");
            }
        });

        e.preventDefault();
    });

    $("a[name='btn_flyingfish_publish']").on("click", function (e) {
        var expt_id = $(this).data("expt-id");

        $.colorbox({
            href: "/flyingfish/" + expt_id + "/publish/",
            fastIframe: false,
            overlayClose: false,
            closeButton: true,
            opacity: 0.7,
            width: 750,
            height: "90%",
            title: function () {
                return "<img src='/static/img/logo.png' style='width:100px;'>"
            },
            onComplete: function () {
                //$('#id_start_date').daterangepicker({
                //    singleDatePicker: true,
                //    locale: {
                //        format: 'YYYY-MM-DD'
                //    }
                //});

                /*$('#id_end_date').daterangepicker({
                    singleDatePicker: true,
                    locale: {
                        format: 'DD-MM-YYYY'
                    }
                });*/

                $("#btn_flyingfish_submit").on("click", function (e) {
                    var $this = $(this);
                    var $form = $(".flyingfish_container").find("form");

                    var is_checked = true;
                    var requiredFields = [
                        {key: 'title', value: 'Title'},
                        {key: 'description', value: 'Description'},
                        {key: 'need_participant_num', value: 'Need participant num'},
                        //{key: 'start_date', value: 'Start date'},
                        //{key: 'end_date', value: 'End date'},
                        {key: 'duration', value: 'Approximate duration (minutes)'},
                        {key: 'contact', value: 'Contact Email'},
                        {key: 'reward', value: 'Reward'}
                    ];

                    $.each(requiredFields, function(index, item){
                        var $target = $("#id_" + item.key);
                        if(!$target.val()){
                            var message = item.value + " field is required";
                            new PNotify({
                                title: "Flying Fish",
                                text: message,
                                type: "error"
                            });
                            is_checked = false;
                            $target.focus();
                            return false;
                        }
                    });

                    if(is_checked){
                        $.ajax({
                            url: $form.attr("action"),
                            data: $form.serialize(),
                            dataType: "json",
                            type: "POST",
                            beforeSend: function (xhr) {
                                $this.prop("disabled", true);
                                xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                            },
                            success: function (data) {
                                if(data.status == "form_error"){
                                    var requiredFields = [
                                        {key: 'title', value: 'Title'},
                                        {key: 'description', value: 'Description'},
                                        {key: 'need_participant_num', value: 'Need participant num'},
                                        //{key: 'start_date', value: 'Start date'},
                                        {key: 'duration', value: 'Approximate duration (minutes)'},
                                        {key: 'contact', value: 'Contact Email'},
                                        {key: 'reward', value: 'Potential bonus'},
                                        {key: 'publish_site', value: 'Publish site'},
                                        {key: 'remuneration_per_person', value: 'Remuneration per person'}
                                    ];

                                    $.each(data.message.split(","), function (idx, key) {
                                        $.each(requiredFields, function(index, item){
                                            if(key == item.key){
                                                var $target = $("#id_" + item.key);
                                                var message = item.value + " field is required";
                                                new PNotify({
                                                    title: "Flying Fish",
                                                    text: message,
                                                    type: "error"
                                                });
                                                $target.focus();
                                                return false;
                                            }
                                        });
                                    });
                                }else{
                                    new PNotify({
                                        title: "Flying Fish",
                                        text: data.message,
                                        type: data.status
                                    });
                                    $.colorbox.close();
                                }
                            },
                            error: function (xhr, status, error) {
                                console.log(xhr.responseText);
                            },
                            complete: function(){
                                $this.prop("disabled", false);
                            }
                        });
                    }
                    e.preventDefault();
                });

                $("#btn_add_restriction").on("click", function (e) {
                    var restriction_text = $("#restriction_option").find("option:selected").text();
                    var restriction_name = $("#restriction_option").val();
                    var restriction_value = $("#restriction_content").val();

                    if (restriction_name && restriction_text && restriction_value) {
                        var obj = {
                            "sequence": "#",
                            "restriction_name": restriction_name,
                            "restriction_text": restriction_text,
                            "short_restriction_value": restriction_value.trimToLength(35),
                            "restriction_value": restriction_value
                        };
                        $('#restriction_option').prop('selectedIndex', 0);
                        $('#restriction_content').val('');
                        var tr = _.template($("#tpl_restriction_table").html(), obj);
                        $("#restriction_table").find("tbody").append(tr);
                        refresh_restriction_sequence();
                        save_restriction_data();
                    } else {
                        new PNotify({
                            title: "Restriction",
                            text: "Please enter the correct restriction type and content",
                            type: "info"
                        });
                    }
                    e.preventDefault();
                });

                $("#restriction_table").on("click", "a[name='btn_remove_restriction']", function () {
                    $(this).parents("tr").remove();
                    refresh_restriction_sequence();
                    save_restriction_data();
                });

                $("#btn_flyingfish_close").on("click", function (e) {
                    $.colorbox.close();
                    e.preventDefault();
                });

                init_restriction_table();

                function init_restriction_table() {
                    var restrictionsText = $("#id_restrictions").val();
                    if (restrictionsText) {
                        var jsonData = JSON.parse(restrictionsText);

                        $.each(jsonData, function (idx, item) {
                            var obj = {
                                "sequence": "#",
                                "restriction_name": item.name,
                                "restriction_text": item.text,
                                "short_restriction_value": String(item.value).trimToLength(35),
                                "restriction_value": String(item.value)
                            };

                            var tr = _.template($("#tpl_restriction_table").html(), obj);
                            $("#restriction_table").find("tbody").append(tr);
                            refresh_restriction_sequence();
                        });
                    }
                }

                function refresh_restriction_sequence() {
                    $("#restriction_table").find("tbody tr").each(function (i, item) {
                        $(item).find("td:eq(0)").text(i + 1);
                    });
                }

                function save_restriction_data() {
                    var data = [];
                    $("#restriction_table").find("tbody tr").each(function (i, item) {
                        var restriction_name = $(item).find("td:eq(1)").data("restriction-name");
                        var restriction_text = $(item).find("td:eq(1)").text();
                        var restriction_value = $(item).find("td:eq(2)").data("restriction-value");
                        data.push(
                            {
                                name: restriction_name,
                                text: restriction_text,
                                value: restriction_value
                            }
                        );
                    });
                    $("#id_restrictions").val(JSON.stringify(data));
                }
            }
        });

        e.preventDefault();
    });
});

(function ($) {
    var class_name = 'flash-hide';
    $.fn.extend({
        flashHide: function () {
            return this.each(function () {
                $(this).addClass(class_name);
            });
        },
        flashShow: function () {
            return this.each(function () {
                $(this).removeClass(class_name);
            });
        }
    });
})(jQuery);

function create_mturk_question_modal(url) {
    $.colorbox({
        href: url,
        fastIframe: false,
        overlayClose: false,
        closeButton: true,
        opacity: 0.7,
        width: 750,
        height: "90%",
        title: function () {
            return "<img src='/static/img/logo.png' style='width:100px;'>"
        },
        onComplete: function () {
            $("#btn_mturk_submit").on("click", function (e) {
                var $this = $(this);
                var $form = $(".mechanical_turk_form").find("form");
                $.ajax({
                    url: $form.attr("action"),
                    data: $form.serialize(),
                    dataType: "json",
                    type: "POST",
                    beforeSend: function (xhr) {
                        $this.prop("disabled", true);
                        xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                    },
                    success: function (data) {
                        $("#mt_id").val(data.object_id);
                        if(data.status == "form_error"){
                            var message = "";
                            $.each(data.message.split(","), function () {
                                var $target = $("#id_" + this);
                                var field_text = $target.parent().find("label").text();
                                if (!field_text) {
                                    field_text = $target.attr("placeholder");
                                }
                                message += "'" + field_text + "' ";
                                $target.focus();
                            });
                            message += "field is required";
                            new PNotify({
                                title: "Mechanical Turk",
                                text: message,
                                type: "error"
                            });
                        }else{
                            new PNotify({
                                title: "Mechanical Turk",
                                text: data.message,
                                type: data.status
                            });
                        }
                    },
                    error: function (xhr, status, error) {
                        console.log(xhr.responseText);
                    },
                    complete: function(){
                        $this.prop("disabled", false);
                    }
                });
                e.preventDefault();
            });

            $("#btn_mturk_close").on("click", function (e) {
                $.colorbox.close();
                e.preventDefault();
            });

            var init_data = [];

            $.each($("#id_country").val().split(","), function () {
                if($.trim(this)){
                    init_data.push({id: this, text: this });
                }
            });

            $("#id_country").select2({
                placeholder: "Select Country",
                minimumInputLength: 1,
                allowClear: true,
                multiple: true,
                formatInputTooShort: function () {
                    return "Please enter your required country codes";
                },
                ajax: {
                    quietMillis: 150,
                    url: "/country/q/",
                    dataType: "json",
                    data: function (term, page) {
                        return {
                            q: term,
                            page_size: 10,
                            page: page
                        };
                    },
                    results: function (data, page) {
                        var more = (page * 10) < data.total;
                        return { results: data.result, more: more };
                    }
                }
            });

            //$("#select2-drop-mask").click();
            console.log(init_data);
            $('#id_country').select2('data', init_data )
        }
    });
}