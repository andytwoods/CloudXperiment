var propGridHelper = ( function () {
    var api = {};
    var props;
    var unspecified_props_sorted = false;
    var pg = $("#pg");

    var xptParams;
    var toAS3;

    var requestFutureSetup = false;

    var filenameList;

    var moreProps = ' more properties ';

    var propertygrid_info = document.getElementById("propertygrid_info");

    function setInfo(txt){
        propertygrid_info.innerHTML = txt;
    }

    api.setup = function (_xptParams, _toAS3) {
        xptParams = _xptParams;
        toAS3 = _toAS3;
        //if(!unspecified_props_sorted == false) fleshOutInfo();
    };

    api.sortFilenames = function (){
        filenameList = get_attachment_file_list();
    };

    api.update = function (obj) {
        props = obj;
        api.sortFilenames();
        if (requestFutureSetup) {
            requestFutureSetup = false;
            setupGrid();
        }
        else{
            //should really reload data but pg.reload() not working for some reason
            setupGrid();
        }
    };

    api.auto_propertygird_width = function(){
        auto_pg_width();
    }

    function get_attachment_file_list(){
        var file_list = $('.media-list .media .pull-left.attachment_thumb .media-object.experiment-attachment').map(function(){
            str = $(this).attr('alt');
            return {"value":str,"text":str};
        }).get();
        return file_list;
    }

    function auto_pg_width() {
        var offset = 10;
        var width = $("#left_splitter").width() - $("#left_splitter").find("ul:first").width() - offset;
        $("#pg").propertygrid("resize", {"width": width});
    }

    function setupGrid() {
        if (props) {

            fleshOutInfo(); //only needs to be called once

            var myData = JSON.stringify(process_json_data(props));

            pg.propertygrid({
                url: "/propertygrid/json/",
                queryParams: {data: myData},
                method: "POST",
                scrollbarSize: 0,
                showGroup: true,
                striped:false,
                singleSelect:true,
                showFooter:true,
                resizable:true,
                width: 9999,
                groupFormatter: groupFormatter,
                nowrap:false,
                autoRowHeight:true,
                columns: [
                    [
                        {field: "name", title: "name", width: 100, sortable: true, formatter: function (value, row, index) {
                            var $content = $("<span></span>");
                            $content.html(value);
                            if (row.tooltip && row.tooltip != undefined) {
                                $content.attr("data-tooltip", row.tooltip);
                                $content.addClass("easyui-tooltip");
                            }
                            return $("<p>").append($content.eq(0).clone()).html()
                        }},
                        {field: "value", title: "value", width: 100, resizable: false}
                    ]
                ],
                onLoadSuccess: function () {
                    pg.datagrid("getPanel").find(".easyui-tooltip").each(function () {
                        var content = $(this).attr("data-tooltip");
                        if (content) {
                            $(this).tooltip({
                                content: content,
                                position: "right"
                            });
                        }
                    });
                    auto_pg_width();
                },
                onBeginEdit: function (rowIndex, rowData) {
                    var editors = pg.propertygrid('getEditors', rowIndex);
                    for (var i = 0; i < editors.length; i++) {
                        var editor = editors[i];
                        $(editor.target).bind("keyup", function (e) {
                            var code = e.keyCode || e.which;
                            if (code == 13) {
                                pg.propertygrid('endEdit', rowIndex);
                            }
                        });
                    }
                },
                onEndEdit: function (index, row) {
                    //console.log(row)
                    //future, logic here to prevent updates when nothing has changed.
                    row.name = removeHTML(row.name)
                    toAS3('propEdit',row);
                }
            });
        }else {
            requestFutureSetup = true;
        }

      //  console.log( props);
    }

    function removeHTML(_html){
         var div = document.createElement('div');
         div.innerHTML = _html;
         return div.innerText || div.textContent;
    }

    function groupFormatter(fvalue, rows) {
        // console.log(rows.options)
        return '<span style="white-space:pre">' + fvalue + '</span>  <span style="color:red; cursor:pointer" id="SpecialSpan",  onclick="propGridHelper.morePropL(this)">' + moreProps + '</span>'
    }

    api.morePropL = function (ele) {
        if (!xptParams)return;
        ele = ele.parentNode;

        var peg = ele.innerText || ele.textContent;
        if (!peg) return;
        var txt = peg.split("— ")[1].split(" ")[0];

        //if(propGridHelper.hasOwnProperty('unspecified_props') == false) return;
        log(txt,xptParams[txt])
        for(var k in xptParams){
            log(k,2)
        }
        var props = xptParams[txt].attrsInfo;

        var arr = [];
        for (var key in props) {
            arr.push(toolTipper(key, txt, peg));
        }
        arr.sort();
        setInfo(arr.join(", "))
    };

    function toolTipper(key, stim,peg){
        return "<a peg='"+peg+"' stim='"+stim+"'  style='cursor:pointer;' onclick=propGridHelper.infoBox(this)>"+key+"</a>"
    }

    api.infoBox = function (ele) {

        var peg = ele.getAttribute('peg');
        var stim = ele.getAttribute('stim');
        var prop = ele.innerText || ele.textContent;
        var info

        if (xptParams[stim].attrsInfo.hasOwnProperty(prop) == false) {
            info = {type: 'string', defaultVal: '', possibleVals: ''}
        }
        else info = xptParams[stim].attrsInfo[prop];

        var table = "<table class='table'><tr><td>type</td><td>" + info.type +
            "</td></tr><tr><td>defaultVal</td><td>" + addable(info.defaultVal, null) +
            "</td></tr><tr><td>Possible vals</td><td>" + addable(info.possibleVals, '||') +
            "</td></tr></table>";

        var addRemove = '';
        if (prop != 'peg') addRemove = " (" + getTitle('add', info.defaultVal) + " " + getTitle('remove', 'REMOVE_ATTRIB') + ")</b></p>";
        messager("<p><b>" + stim + "." + prop + addRemove + table + "<p>" + info.info + "</p>");

        function addable(txt, split) {
            var arr;
            if (!txt) return '';
            if (split == null) {
                arr = [];
                arr[0] = txt;
            }
            else {
                log(111, txt, split);
                arr = txt.split(split);
            }
            for (var i = 0; i < arr.length; i++) {
                arr[i] = getTitle(arr[i], arr[i]);
            }
            return arr.join("");
        }

        function getTitle(_txt, val) {
            return "<a val='" + val + "' prop='" + prop + "' peg='" + peg + "' style='cursor:pointer;' onclick=propGridHelper.addAttrib(this)>" + _txt + "</a>";
        }

    };

    api.addAttrib = function (ele) {
        var group = ele.getAttribute('peg').toString();
        if (group.indexOf('more properties') != -1)   group = group.substr(0, group.length - moreProps.length + 1);

        var name = ele.getAttribute('prop');
        var value = ele.getAttribute('val');

        if (value == 'REMOVE_ATTRIB') {
            toAS3('propRemove', {group: group, name: name, value: value});
        }
        else {
            toAS3('propAdd', {group: group, name: name, value: value});
        }
    };



    function process_json_data(json_obj) {
        var result = {"total": json_obj.total, "rows": []};

        //Hi Andy, this is an example, you can refer to it
        /*props = {"total": 33, "rows": [
            {"detailedName": "addText", "value": "true", "name": "select-test", "group": "example", "type": "select", "data": [
                {"value": "true", "text": "true"},
                {"value": "false", "text": "false"}
            ], "tooltip": "test"},
            {"detailedName": "addText", "value": "50", "name": "number-test", "group": "example", "type": "number", "min": 5, "max": 200},
            {"detailedName": "addButton", "value": "test", "name": "rich-editor-test", "group": "example", "type": "richtext"},
            {"detailedName": "addButton", "value": "#5b8088", "name": "color-test", "group": "example", "type": "color"},
            {"detailedName": "addButton", "value": "10%", "name": "percent-test", "group": "example", "type": "percent"},
            {"detailedName": "addButton", "value": "2014-11-05", "name": "date-test", "group": "example", "type": "date"},
            {"detailedName": "addButton", "value": "andy@gmail.com", "name": "email-test", "group": "example", "type": "email"},
            {"detailedName": "addButton", "value": "", "name": "file-test", "group": "example", "type": "file"}
        ]};*/


        function tip(peg, key, stim){
            return "<a peg='"+peg+"' stim='"+stim+"'  style='cursor:pointer;' onclick=propGridHelper.infoBox(this)>"+key+"</a>";
        }

        $.each(json_obj.rows, function (index, row) {

            var item = { "value": row.value, "group": row.group, "tooltip": row.tooltip};
            var arr = row.group.split("— ");
            item.name =  tip(row.group,row.name,arr[1].split(" ")[0]);
            var rowName= row.name.toLowerCase();

            if(row.value.indexOf(";")!=-1 || row.value.indexOf("---")!=-1) row.type = 'text';
            else if (rowName.indexOf('colour') != -1) row.type = 'color';
            else if(rowName.indexOf("filename")!=-1) row.type = "file";
            else if(rowName == 'text')row.type= 'richtext';
            else if(rowName=='x' || rowName=='y'|| rowName=='width'|| rowName=='height'){
                   if(row.value.indexOf("%")!=-1)   row.type='text';
            }
            else if(rowName=='howmany'){
                row.type = 'number';
                item.min=0;
            }
            if (row.type) {
                //console.log(row.type)
                switch (row.type) {
                    case "text":
                        item.editor = {"type": "validatebox", "options": {}};
                        if (row.length) {
                            item.editor.options.validType = {"length": row.length};
                        }
                        if (row.required) {
                            item.editor.options.required = row.required;
                        }
                        break;
                    case "file":
                        item.editor = {"type": "combobox", "options": {}};
                        item.editor.options.data = get_attachment_file_list();
                        item.editor.options.panelHeight = "auto";
                        break;
                    case "number":
                        item.editor = {"type": "numberspinner", "options": {}};
                        if (row.min) {
                            item.editor.options.min = row.min;
                        }
                        if (row.max) {
                            item.editor.options.max = row.max;
                        }
                        if (row.required) {
                            item.editor.options.required = row.required;
                        }
                        break;
                    case "color":
                        item.editor = {"type": "colorpicker", "options": {}};
                        if (row.editable) {
                            item.editor.options.editable = row.editable;
                        }
                        if (row.required) {
                            item.editor.options.required = row.required;
                        }
                        break;
                    case "date":
                        item.editor = {"type": "datebox", "options": {}};
                        if (row.editable) {
                            item.editor.options.editable = row.editable;
                        }
                        if (row.required) {
                            item.editor.options.required = row.required;
                        }
                        break;
                    case "select":
                        item.editor = {"type": "combobox", "options": {}};
                        if (row.data) {
                            item.editor.options.data = row.data;
                            item.editor.options.panelHeight = "auto";
                        }
                        break;
                    case "email":
                        item.editor = {"type": "validatebox", "options": {}};
                        item.editor.options.validType = {"email": true};
                        if (row.length) {
                            item.editor.options.validType.length = row.length;
                        }
                        if (row.required) {
                            item.editor.options.required = row.required;
                        }
                        break;
                    case "richtext":
                        item.editor = {"type": "ckeditor", "options": {}};
                        if (row.editable) {
                            item.editor.options.editable = row.editable;
                        }
                        if (row.required) {
                            item.editor.options.required = row.required;
                        }
                        break;
                    case "percent":
                        item.editor = {"type": "percent", "options": {}};
                        if (row.length) {
                            item.editor.options.validType = {"length": row.length};
                        }
                        if (row.required) {
                            item.editor.options.required = row.required;
                        }
                        break;
                }
            } else {
                item.editor = row.editor;
            }

            result.rows.push(item);
        });

        return result;
    }

    function fleshOutInfo() {

        if (xptParams) {
            unspecified_props_sorted = true;

            var row;
            var detailedName = '';
            var param;
            var foundBigParams = {};

            for (var i = 0; i < props.rows.length; i++) {
                row = props.rows[i];
                param = row.name;

                if (detailedName != row.detailedName) {
                    detailedName = row.detailedName;
                    //console.log(detailedName);
                    if (xptParams.hasOwnProperty(detailedName)) {
                        foundBigParams[detailedName] = jQuery.extend(true, {}, xptParams[detailedName].attrsInfo);
                    } //deep copy
                }
                if (foundBigParams.hasOwnProperty(detailedName)) populateRow(row.detailedName, foundBigParams[detailedName], row);
            }
        }
    }

    function populateRow(stim, largeInfo, smallInfo) {

        var nam = smallInfo.name;

        var spec;
        if (largeInfo.hasOwnProperty(nam)) {
            spec = jQuery.extend(true, {}, largeInfo[nam]); //deep copy
            //delete largeInfo[nam]; //so we can collect unspecified attribs
        }

        else {
            spec = {"type": "string", "info": ""}
        }

        if (nam == "peg") {
            spec.type = 'text';
            spec.info = 'this is the unique ID of the stimulus or object.';
        }

        smallInfo.type = spec.type;
        smallInfo.info = spec.info;
        smallInfo.defaultVal = spec.defaultVal;
        if (spec.hasOwnProperty('data'))    smallInfo.data = generateData(spec.possibleVals);

        if (spec) {
            switch (spec.type) {
                case "string":
                    smallInfo.type = "text";
                    break;
                case "boolean":
                    smallInfo.data = [
                        {"value": "true", "text": "true"},
                        {"value": "false", "text": "false"}
                    ];
                    smallInfo.type = "select";
                    break;
                case "int":
                case "number":
                case "uint":
                    smallInfo.type = "text";
                    break;

            }
        }
    }

    function generateData(str) {
        if (!str || str.length == 0)return [];
        var data = [];
        var split = str.split("|");

        for (var i = 0; i < split.length; i++) {
            data.push({"value": split[i], "text": split[i]});
        }

        return data;
    }

    $.fn.datebox.defaults.formatter = function (date) {
        var y = date.getFullYear();
        var m = date.getMonth() + 1;
        var d = date.getDate();
        return y + '-' + (m < 10 ? '0' + m : m) + '-' + (d < 10 ? '0' + d : d);
    };

    $.fn.datebox.defaults.parser = function (s) {
        if (s) {
            var a = s.split('-');
            var d = new Date(parseInt(a[0]), parseInt(a[1]) - 1, parseInt(a[2]));
            return d;
        } else {
            return new Date();
        }
    };

    $.extend($.fn.propertygrid.defaults.editors, {
        colorpicker: {
            init: function (container, options) {
                var target = $('<input class="pg-colorpicker">').appendTo(container);
                var $parent = target.parents("tr.datagrid-row");
                var data = $("#pg").propertygrid("getData").rows[$parent.attr("datagrid-row-index")];

                target.ColorPicker({
                    color: data.value,
                    onShow: function (colpkr) {
                        $(colpkr).show();
                        return false;
                    },
                    onHide: function (colpkr) {
                        $(colpkr).remove();
                        toAS3('propEdit',data);
                        return false;
                    },
                    onChange: function (hsb, hex, rgb) {
                        $parent.find("td:eq(1) > div").text("#" + hex);
                        data.value = "#" + hex;

                    }
                });

                target.click();

                return target;
            },
            destroy: function (target) {
                $(target).remove();
            },
            getValue: function (target) {
                return $(target).val();
            },
            setValue: function (target, value) {
                $(target).val(value);
            },
            resize: function (target, width) {
                $(target)._outerWidth(width);
            }
        }
    });

    $.extend($.fn.propertygrid.defaults.editors, {
        ckeditor: {
            init: function (container, options) {
                var target = $('<input>').appendTo(container);
                var $parent = target.parents("tr.datagrid-row");
                var row_index = $parent.attr("datagrid-row-index");
                var data = $("#pg").propertygrid("getData").rows[row_index];
                data.name = removeHTML(data.name);
                var ckeditor_id = "ckeditor_" + row_index;
                var content = $('<div class="pg-ckeditor" style="display: none;"><textarea id="' + ckeditor_id + '"/></div>').appendTo("body");

                CKEDITOR.config.coreStyles_bold = { element : 'b', overrides : 'strong' };
                CKEDITOR.config.enterMode = CKEDITOR.ENTER_BR;
                CKEDITOR.config.coreStyles_italic = { element : 'i', overrides : 'em' };
                CKEDITOR.config.toolbarGroups = [
                    { name: 'clipboard',   groups: [ 'clipboard', 'undo' ] },
                    { name: 'editing',     groups: [ 'find', 'selection', 'spellchecker' ] },
                    { name: 'links' },
                    { name: 'insert' },
                    { name: 'forms' },
                    { name: 'tools' },
                    { name: 'document',    groups: [ 'mode', 'document', 'doctools' ] },
                    { name: 'others' },
                    '/',
                    { name: 'basicstyles', groups: [ 'basicstyles', 'cleanup' ] },
                    { name: 'paragraph',   groups: [ 'list', 'indent', 'blocks', 'align' ] },
                    { name: 'styles' },
                    { name: 'colors' },
                    { name: 'about' }
                ];

                target.bind("click", function () {
                    if (content.css("display") != "block") {
                        var height = 369;
                        var width = 700;
                        var pos = $(this).offset();
                        var top = pos.top + this.offsetHeight;
                        var left = pos.left;
                        var m = document.compatMode == 'CSS1Compat';
                        var viewPort = {
                            l: window.pageXOffset || (m ? document.documentElement.scrollLeft : document.body.scrollLeft),
                            t: window.pageYOffset || (m ? document.documentElement.scrollTop : document.body.scrollTop),
                            w: window.innerWidth || (m ? document.documentElement.clientWidth : document.body.clientWidth),
                            h: window.innerHeight || (m ? document.documentElement.clientHeight : document.body.clientHeight)
                        };
                        if (top + height > viewPort.t + viewPort.h) {
                            top -= this.offsetHeight + height;
                        }
                        if (left + width > viewPort.l + viewPort.w) {
                            left -= width;
                        }
                        content.css({"left": left + "px", "top": top + "px"});
                        content.css({"width": width + "px", "height": height + "px"});
                        content.css("display", "block");
                        CKEDITOR.replace(ckeditor_id, {
                            language: "en",
                            height: "193px"
                        });
                        var val = data.value;
                        val = val.split("}").join(">");
                        val = val.split("{").join("<");
                        CKEDITOR.instances[ckeditor_id].setData(val);
                        content.attr("data-ckeditor-id", ckeditor_id);
                    }
                });

                $(document).bind("mousedown", downHandler);

                function downHandler(e) {
                    var is_show = false;
                    var ckeditor_id = content.attr("data-ckeditor-id");
                    if (content == e.target) {
                        is_show = true;
                    } else if ($parent.has(e.target).length) {
                        is_show = true;
                    } else if (content.has(e.target).length) {
                        is_show = true;
                    } else if ($(".cke_dialog_body").has(e.target).length) {
                        is_show = true;
                    }
                    if (!is_show) {
                        var ckeditor_content = CKEDITOR.instances[ckeditor_id].getData();
                        ckeditor_content = ckeditor_content.split(">").join("}");
                        ckeditor_content = ckeditor_content.split("<").join("{");

                        $parent.find("td:eq(1) > div").text(ckeditor_content);
                        data.value = ckeditor_content;
                        if(data.value.substr(data.value.length-6)=='&nbsp;'){
                            data.value = data.value.substr(1,data.value.length-7);
                        }
                       // log(111,data.value)
                        toAS3('propEdit', data);
                        //CKEDITOR.instances[ckeditor_id].destroy();
                        content.remove();
                        $(document).unbind("mousedown", downHandler);
                    }
                }

                target.click();

                return target;
            },
            destroy: function (target) {
                $(target).remove();
            },
            getValue: function (target) {
                var val = $(target).val();
                return val;
            },
            setValue: function (target, val) {

                $(target).val(val);
            },
            resize: function (target, width) {
                //$(target)._outerWidth(width);
            }
        }
    });

    $.extend($.fn.datagrid.defaults.editors, {
        percent: {
            init: function (container, options) {
                var target = $('<input type="text" class="datagrid-editable-input">').appendTo(container);
                var $parent = target.parents("tr.datagrid-row");
                var data = $("#pg").propertygrid("getData").rows[$parent.attr("datagrid-row-index")];
                target.attr("data-origin", data.value);
                return target;
            },
            destroy: function (target) {
                $(target).remove();
            },
            getValue: function (target) {
                var origin_text = $(target).attr("data-origin");
                var result = $(target).val();
                if (result.indexOf("%") != -1) {
                    result = result.split("%")[0];
                }
                var parse_text = parseInt(result);
                if (result && !isNaN(parse_text)) {
                    result = parse_text + "%";
                } else {
                    result = origin_text;
                }
                return result;
            },
            setValue: function (target, value) {
                if (value.indexOf("%") != -1) {
                    var text = value.split("%")[0];
                    var parse_text = parseInt(text);
                    if (text && !isNaN(parse_text)) {
                        $(target).val(parse_text);
                    }
                } else {
                    var parse_text = parseInt(value);
                    if (value && !isNaN(parse_text)) {
                        $(target).val(parse_text + "%");
                    }
                }
            },
            resize: function (target, width) {
                $(target)._outerWidth(width);
            }
        }
    });

    $("#propertygrid").on("click", function () {
        //log("clicked");
        setupGrid();
    });

    return api;
}());
