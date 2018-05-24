$(document).ready(function () {
    $("#main_splitter").jqxSplitter({
        theme: "office",
        width: "100%",
        height: 1200,
        panels: [
            { size: "21%" },
            { size: "79%" }
        ]
    });

    $("#right_splitter").jqxSplitter({
        theme: "office",
        height: "100%",
        orientation: "horizontal",
        panels: [
            { size: "15%" },
            { size: "85%", collapsible: false }
        ]
    });

    $("#right_bottom_splitter").jqxSplitter({
        theme: "office",
        height: "100%",
        panels: [
            { size: "65%", min: 600, collapsible: false },
            { size: "35%", min: 400 }
        ]
    });

    $("#right_bottom_left_splitter").jqxSplitter({
        theme: "office",
        height: "100%",
        orientation: "horizontal",
        panels: [
            { size: "80%", collapsible: false },
            { size: "20%" }
        ]
    });

    $('#right_bottom_splitter').on('resize', function (event) {
        //timelineHelper.command("fit-everything");
        timelineHelper.command("zoom-out");
    });

    $("#main_splitter").on('resize', function (event) {
        propGridHelper.auto_propertygird_width();
    });

    $('#right_splitter').on('resize', function (event) {
        var height = $("#right_bottom_right_splitter").height() - 54;
        $("#multi_trial").height(height);
    });
});