$(function () {
    window.data_dict = {
        q: "",
        page: 1,
        page_size: 5
    };

    $("#snippets").on("click", function(){
        $.colorbox({
            href: "/snippet/modal/",
            fastIframe: false,
            opacity: 0.7,
            width: "80%",
            height: "90%",
            title: function () {
                return "<img src='/static/img/logo.png' style='width:100px;'>"
            },
            onComplete: function () {
                /*$("#snippet_select").select2({
                    placeholder: "Select Snippet",
                    minimumInputLength: 1,
                    allowClear: true,
                    multiple: true,
                    ajax: {
                        quietMillis: 150,
                        url: "/snippet/query/",
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
                });*/

                $("#snippet_search").on("click", function(){
                    $("#snippet_list").html("");
                    data_dict.page = 0;
                    data_dict.q = $("#snippet_select").val();
                    $("#snippet_more").trigger("click");
                });

                $("#snippet_more").on("click", function () {
                    var $this = $(this);
                    var $container = $("#snippet_list");
                    data_dict.page += 1;
                    $.ajax({
                        type: 'GET',
                        dataType: 'html',
                        url: '/snippet/ajax/more/',
                        data: data_dict,
                        beforeSend: function (xhr) {
                            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                            disable_button($this);
                        },
                        success: function (data) {
                            var prev_count = $container.find(".row").length;
                            $container.append(data);
                            var current_count = $container.find(".row").length;
                            if (current_count - prev_count >= data_dict.page_size) {
                                enable_button($this);
                            }
                        }
                    });
                });

                $("#snippet_list").on("click", "a[name='snippet_list']", function () {
                    var $this = $(this);
                    var snippet_id = $this.data("id");

                    $.ajax({
                        type: 'GET',
                        url: '/snippet/ajax/like/' + snippet_id + '/',
                        dataType: 'json',
                        beforeSend: function (xhr) {
                            xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
                        },
                        success: function (result) {
                            if (result.status == "success") {
                                $this.removeAttr("name").removeAttr("data-id");
                                $this.attr("disabled", "disabled");
                                $this.addClass("disabled");
                                var $like_count = $this.find(".like_count");
                                $like_count.text(parseInt($like_count.text()) + 1);
                            } else {
                                alert(result.message);
                            }
                        }
                    });
                    return false;
                });
            }
        });
    });

    $("#snippet_keyword").tagit();

    $("#snippet_form").submit(function () {
        $("#id_keyword").val($("#snippet_keyword").tagit("assignedTags").toString());
        $.ajax({
            url: "/snippet/upload_snippet/",
            type: "POST",
            dataType: "json",
            data: $("#snippet_form").serialize(),
            async: true,
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", $.cookie("csrftoken"));
            },
            success: function (result) {
                if (result.status == "success") {
                    $("#create_snippet_modal").modal("hide");
                }else{
                    console.log(result.message);
                    $("#create_snippet_modal").modal("hide");
                }
            }
        });
        return false;
    });
});

function disable_button(obj) {
    $(obj).attr('disabled', 'disabled');
    $(obj).hide();
}

function enable_button(obj) {
    $(obj).removeAttr('disabled');
    $(obj).show();
}