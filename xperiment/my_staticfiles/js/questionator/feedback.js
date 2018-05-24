var stats = ( function () {
    var api = {}

    api.calc = function(list, data){
        var item;
        var obj = {};
        for(var i = 0;i<list.length;i++){
            item = list[i];
            if(api.hasOwnProperty(item)){
                obj[item] = api[item](data);
            }
        }
        return obj;
    };

    api.two_stderr = function(data){
        console.log(data)
        var stdev = api.stdev(data);
        var count = data.length;
        return 2 * stdev / Math.sqrt(count);
    }

    api.mean = function(data){
        var total = 0;
        for(var i=0;i<data.length;i++){
            total += parseFloat(data[i]);
        }
        return total / data.length;
    };

    api.sum = function(data){
        var total = 0;
        for(var i = 0;i<data.length;i++){
            total+=data[i];
        }
        return total;
    }

    api.stdev = function(data){
        var avg = api.mean(data);

        var squareDiffs = data.map(function(value){
            var diff = value - avg;
            var sqrDiff = diff * diff;
            return sqrDiff;
        });

        var total = api.sum(squareDiffs);

        return Math.sqrt(total / (data.length-1));
;
    };





    return api;
}());


var processdata = ( function() {
    var api = {}

    var q_id='results_q';
    var images_id = 'http';

    var keep_row=[q_id, images_id];

    api.DO = function(raw, callback_per_question){

        var raw_row;
        var row;
        var data = [];

        for(var i=0;i<raw.length;i++){
            raw_row = raw[i];
            row = prune_row(raw_row)
            if(row != null)data.push(row)
        }
        var combined_data = combined(data);
        /*
        {question:
            {imageurl: [data]} }*/

        if(callback_per_question!=undefined){
            for(var key in combined_data){
                callback_per_question(key, combined_data[key]);
            }
        }
    };

    function combined(data){
        var combined = {};
        var i;
        var row;
        var key;
        var q;
        for(i=0;i<data.length;i++){
            row = data[i];
            if(row.hasOwnProperty(q_id)) {
                q = row[q_id];
                if(combined.hasOwnProperty(q)==false){
                    combined[q] = {};
                }
                for (key in row) {
                    if(key!=q_id){
                        if(combined[q].hasOwnProperty(key)==false){
                            combined[q][key] = [];
                        }
                        combined[q][key].push( row[key] );
                    }
                }
            }
        }
        return combined;
    }



    function prune_row(row){
        var cleaned_row;
        var found;
        var keep_i;
        for(var key in row){
            found = false;
            for(keep_i=0;keep_i<keep_row.length;keep_i++){
                keep = keep_row[keep_i];
                if(key.indexOf(keep)!=-1){
                    found = true;
                    break;
                }
            }
            if(found){
                if(cleaned_row == undefined) cleaned_row = {};
                cleaned_row[key] = row[key];
            }
        }

        return cleaned_row;
    }

    return api;
}());


var barchart = ( function() {

    var api = {};

    var chart = null;
    var config = null;
    api.margin = {top: 20, right: 10, bottom: 20, left: 10};

    api.init = function (container) {
        config = {}
        config.width = $(container).width();
        config.height = 300;//$(container).height(),
        chart = d3.select(container)
            .append("svg:svg")
            .attr("width", config.width)
            .attr("height", config.height);



    };

    api.populate =  function(question, data){
        var means = [];
        var stderrs = [];
        var images = [];
        for(var question in data){
            means.push(data[question]['mean']);
            stderrs.push(data[question]['two_stderr']);
            images.push(question)
        }

        function correcturl(str){
            var arr = str.split("_");
            return arr.join(".");
        }


        var shuffled = [];
        for(var i=0;i<means.length;i++){
            shuffled.push({image:correcturl(images[i]), value:means[i], stderr:stderrs[i], key:i});
        }

        draw( shuffled );
    }

    function draw(data) {

        var w = config.width - api.margin.left - api.margin.right;
        var h = config.height - api.margin.top - api.margin.bottom;
        var margin = 40;



        var key = function (d) {
            return d.key;
        };

        var value = function (d) {
            return d.value;
        };
        console.log(data);


        var xScale = d3.scale.ordinal()
            .domain(d3.range(data.length))
            .rangeRoundBands([40, w], 0.05);

        var yScale = d3.scale.linear()
            .domain([0, 100])
            .range([h - margin - 50, 0]);

        var x_axis = d3.svg.axis().scale(xScale);
        var y_axis = d3.svg.axis().scale(yScale).orient("left");


        d3.select("svg")
            .append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + (h - margin) + ")")
            .call(x_axis);

        d3.select("svg")
            .append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + margin + ",0)")
            .call(y_axis);

//Create bars
        chart.selectAll("rect")
            .data(data, key)
            .enter()
            .append("rect")
            .attr("x", function (d, i) {
                return xScale(i);
            })
            .attr("y", function (d) {
                return yScale(d.value);
            })
            .attr("width", xScale.rangeBand())
            .attr("height", function (d) {
                return (yScale(0) - yScale(d.value));
            })
            .attr("fill", function (d) {
                return "rgb(96, 0, " + (d.value * 1000) + ")";
            })

            //Tooltip
            .on("mouseover", function (d) {
                //Get this bar's x/y values, then augment for the tooltip
                var xPosition = parseFloat(d3.select(this).attr("x")) + xScale.rangeBand() / 2;
                var yPosition = parseFloat(d3.select(this).attr("y")) + 14;

                //Update Tooltip Position & value
                d3.select("#tooltip")
                    .style("left", xPosition + "px")
                    .style("top", yPosition + "px")
                    .select("#value")
                    .text(d.value);
                d3.select("#tooltip").classed("hidden", false)
            })
            .on("mouseout", function () {
                //Remove the tooltip
                d3.select("#tooltip").classed("hidden", true);
            })
        
            .each(function(d,i) {
                chart
                    .append("rect")
                    .attr("x", function () {
                        return xScale(i) + xScale.rangeBand() *.5;
                    })
                    .attr("y", function () {
                        console.log(d)
                        return yScale(d.value+ d.stderr);
                    })
                    .attr("width", 5)
                    .attr("height", function () {
                        return (yScale(0) - yScale(2* d.stderr));
                    })
                    .attr("fill", function () {
                        return "rgb(96, 0, " + (d.value * 100) + ")";
                    })
                    .attr("class", "errbar");
            })
        


//Create labels
        chart.selectAll("text")
            .data(data, key)
            .enter()
            .append("text")
            .text(function (d) {
                return Math.round(d.value * 10)/10;
            })
            .attr("text-anchor", "middle")
            .attr("x", function (d, i) {
                return xScale(i) + xScale.rangeBand() / 2;
            })
            .attr("y", function (d) {
                return yScale(d.value) + 14;
            })
            .attr("font-family", "sans-serif")
            .attr("font-size", "11px")
            .attr("fill", "white");

        var ticks = chart.select(".axis").selectAll(".tick")
                    .data(data)
                    .append("svg:image")
                    .attr("xlink:href", function (d) { return d.image ; })
                    .attr("width", 100)
                    .attr("height", 100)
                    .attr("x", -44)
                    .attr("y", -55)


    };



    return api;
}());
