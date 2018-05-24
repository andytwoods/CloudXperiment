$(function () {
    var mturk_error_count = 0;

    var clip = new ZeroClipboard($("#btn_copy"), {
        moviePath: "/static/js/zeroclipboard/ZeroClipboard.swf"
    });

    clip.on("load", function (client) {
        clip.on("dataRequested", function (client, args) {
            client.setText($("#study_url_content").find("a").attr("title"));
        });
        client.on("complete", function (client, args) {
            new PNotify({
                title: "Copy Link Info",
                text: "Copied study url to clipboard",
                type: "success"
            });
        });
    });

    $("#btn_mturk_check_question").on("click", function () {
        var $this = $(this);
        var mt_id = $this.data("mt-id");
        var assignment_id = $this.data("assignment-id");
        var url = "/mturk/" + mt_id + "/" + assignment_id + "/check/question/";

        $this.prop("disabled", true);

        $.ajax({
            url: url,
            dataType: "json",
            type: "GET",
            success: function (data) {
                var message_type = "error";
                if (data.status == "success") {
                    message_type = "success";
                    setTimeout(function () {
                        location.reload();
                    }, 3000);
                }

                new PNotify({
                    title: "Checked Info",
                    text: data.message,
                    type: message_type
                });

                $this.prop("disabled", false);
            }
        });
    });

    $("a[href^='mailto:']").on("click", function () {
        window.top.location = $(this).prop("href");
        return false;
    });

    $("#btn_submit_mturk").on("click", function () {
        var $this = $(this);
        var assignment_id = $("#assignmentId").val();
        var password = $("#id_password").val();

        if (password) {
            $this.prop("disabled", true);

            $.ajax({
                url: "/api/mturk/password/validate/",
                data: {"assignment_id": assignment_id, "password": password},
                dataType: "json",
                type: "GET",
                success: function (result) {
                    var message_type = "error";
                    if (result.status == "success") {
                        message_type = "success";
                        $("#mturk_form").submit();
                    } else {
                        var second = 0;
                        var button_text = $this.text();

                        mturk_error_count++;

                        if (mturk_error_count <= 1) {
                            second = 5;
                        } else {
                            second = (mturk_error_count - 2) * 10 + 10;
                        }

                        run_time(
                            second,
                            function process(second) {
                                $this.text("Please wait " + second + " seconds");
                            },
                            function complete() {
                                $this.text(button_text);
                                $this.prop("disabled", false);
                            }
                        );
                    }

                    new PNotify({
                        title: "Checked Info",
                        text: result.message,
                        type: message_type
                    });
                }
            });
        } else {
            new PNotify({
                title: "Checked Info",
                text: "Password can not be empty",
                type: "error"
            });
        }
    });

    function run_time(second, process, complete) {
        var interval_id = setInterval(function () {
            if (second == 0) {
                complete();
                clearInterval(interval_id);
                return;
            }
            process(second);
            second--;
        }, 1000);
    }
});
