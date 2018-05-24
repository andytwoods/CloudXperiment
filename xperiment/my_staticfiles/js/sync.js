var connected = false;
var xpt;
var actions = {};

function linkXpt(){


    if(navigator.appName.indexOf("Microsoft")!= -1){
		xpt=window['xperiment']

	}
	else {
		xpt = window.document['xperiment'];

	}

}

function addAction(nam, f){
	actions[nam]=f;
}

function log(str){
	console.log("log:"+Array.prototype.slice.call(arguments).join(" "));//,"\t\t\t calling function:",arguments.callee.caller.name);
}


function toAS3(what, data) {


    //console.log(111222,what, data)

    try {
        if (connected)xpt.toAS3(what, data);
        else log('attempted AS3 communication but not ready yet:',what)
    }
    catch (err) {
        log('Devel', err)
    }
}


function toJS(what,data)
{

	connected=true
    //log(1212,what,data)
	if(what=="linkup" && data == '')toAS3('linkedup','')
	else{
		if(actions.hasOwnProperty(what)){
            log('command',what,'\t\t',JSON.stringify(data).substr(1,30))
            actions[what](data);
        }
		else alert('devel error: command does not exist yet: '+what)
	}
}

addAction('bgCol',bgCol)
function bgCol(col){
    document.body.style.background = col;
}