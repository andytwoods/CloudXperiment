var timelineHelper = ( function()
{

    var api = {};

    api.toAS3 = null;

    var timeline = null;
    var jsonData =
        [
            {
                "start": 10,
                "end": 20,
                "content": "a",
                "group": "group1",
                "type": "range"
            }
        ];

    var groupText = {};
    initStimTypes();

    function initStimTypes() {
        var stimuli = ["button", "combobox", "hideMouse", "inputText", "jpg", "keypress", "LAMS", "lineScale", "loading", "multipleNumberSelector", "sequentialCounter", "shape", "sound", "text", "TMS", "video"];
        var stim;
        for (var i = 0; i < stimuli.length; i++) {
            stim = stimuli[i];
            groupText[stim] = "<img src='/static/css/AcidJs.Ribbon/icons/16/" + stim + ".png' style='width:16px; height:16px; vertical-align: middle'/> ";
        }

        groupText["group1"]= '<img src="/static/css/AcidJs.Ribbon/icons/16/copy.png" style="width:24px; height:24px; vertical-align: middle">Group 1';
    }

    google.load("visualization", "1");

    // Set callback to run when API is loaded
    google.setOnLoadCallback(drawVisualization);

    // Called when the Visualization API is loaded.
    function drawVisualization() {

        var options = {

            //set fixed time which cannot be moved left
            min: new Date(2014, 7, 13, 0, 0, 0),
            max: new Date(2014, 7, 13, 0, 0, 40),

            //default width of the chart ( height is auto )
            width: "100%",

            start: new Date(2014, 7, 13, 0, 0, 0),
            //set if if could be resized
            resizable: true,

            //set if the items are editable
            editable: true,

            eventMargin: 5,  // minimal margin between events
            eventMarginAxis: 0, // minimal margin beteen events and the axis

            showMajorLabels: false, //show detailed time string in axis
            axisOnTop: true,  //otherwise the axis will be at bottom

            //showCustomTime: true, // show a blue, draggable bar displaying a custom time
            //showCurrentTime: true, // show a red bar displaying the current time

            //the width of group label column ( optional )
            groupsWidth: "100px",

            //if allow items move across groups
            groupsChangeable: false,

            //set groups on left or right
            groupsOnRight: false, // or left

            //the minimum range of zoom in
            zoomMin: 10, // 10ms


            //show the navigation panel
            showNavigation: false,

            dragStep:10,

            groupText: groupText, //pass the group name text
            scale: 2,
            step: 5,
            zoomMax: 50000,
            sortableGroup: true,

            playButton:'/static/css/AcidJs.Ribbon/icons/16/play.png', // pls specify button url here
            pauseButton:'/static/css/AcidJs.Ribbon/icons/16/pause.png',
            beginningButton:'/static/css/AcidJs.Ribbon/icons/16/redo.png',
            triangleButton:'/static/css/AcidJs.Ribbon/icons/16/triangle.png',

			playEvent: function () {
                toAS3('playPauseReset_toolbar', {command: 'play'});
				console.log('play button clicked');
			},
			pauseEvent: function () {
                toAS3('playPauseReset_toolbar', {command: 'pause'});
				console.log('pause button clicked');
			},
			beginningEvent: function () {
                toAS3('playPauseReset_toolbar', {command: 'reset'});
				console.log('beginning button clicked');
			},
			triangleEvent: function (time) {
                toAS3('playPauseReset_toolbar', {command: 'goto',time:parseInt(time*1000)});
				//console.log('current time: ' + time);
			}
        };

        // Instantiate our timeline object.


        if (timeline)killTimeLine();
        api.timeline=timeline;
        timeline = new links.Timeline(document.getElementById('mytimeline'));

        timeline.draw(timeline.formatJsonData(options, jsonData), options, true);
        timeline.deleteAllItems(); //a hack


        //confirm on delete
        links.events.addListener(timeline, 'delete', ItemDeleted);
        //on change, update json
        links.events.addListener(timeline, 'change', ItemsUpdated);

        links.events.addListener(timeline, 'reOrdered', ReOrdered);


    }

    function ReOrdered(data) {
        //log(3333,data)
        if(api.toAS3)   api.toAS3('orderChange', data.extra);
    }

    api.setTime = function(time){
        timeline.setTime(time); //'time' variable is ms

    } //your go? yes

    api.command = function(_command) {
        switch (_command) {
            case "zoom-in":
                timeline.zoom(0.4);
                break;
            case "zoom-out":
                timeline.zoom(-0.4);
                break;
            case "shift-left":
                timeline.move(-0.2);
                break;
            case "shift-right":
                timeline.move(+0.2);
                break;
            case "fit-everything":
                timeline.setVisibleChartRangeAuto();
                break;
        }
    }

    api.timelineItems = function(data) {
        //console.log(data)
        timeline.deleteAllItems();
        var item, stim;
        for (var i = 0; i < data.length; i++) {
            stim = data[i];
            item = {};

            item.start = timeline.getDateFromSecond(stim.start/1000);
            if(stim.end=="forever"){
                item.barType="forever";
            }
            item.end = timeline.getDateFromSecond(stim.end/1000);
            item.group = stim.group;
            item.info = "<div style='display:inline-block;' id='peg'>" + stim.info + "</div>";
            item.content =stim.info;
            item.type = "range";

            timeline.addItem(item);

        }
    }

    api.checkResize = function(){
        if(timeline)timeline.checkResize();
    }


    function killTimeLine() {
        if (timeline) {
            timeline.deleteAllItems();
            timeline = null;
        }
    }

    function ItemDeleted(myOptions, myJSON) {
        if (!confirm('Are you sure to delete this item?'))
            timeline.cancelDelete();
        else {
            var list = [];
            var sel = timeline.getSelection();
            for (var i = 0; i < sel.length; i++) {
                if (sel[i] != undefined){

                    //timeline.deleteItem(row);
                    var row = sel[i].row
                    list.push(JSON.stringify(timeline.getData()[row].content));
                   // if(row)  timeline.deleteRow(row)
                }
            }
            if(list.length>0)   api.toAS3("deletePegs",list);
        }
    }


    function ItemsUpdated(myOptions) {
        var selected = timeline.items[timeline.selection.index];
        if(api.toAS3)    api.toAS3("timeChange",{
            "peg":selected.content,
            "start":timeline.getSecondFromDate(selected.start)*1000,
            "end":timeline.getSecondFromDate(selected.end)*1000
        })
    }



    return api;
}());
