var _messenger;
function messager(_html){
    if(!_messenger) {
        _messenger = $('#messenger');
        _messenger.window({
            width: 300,
            height: 300,
            left: "",
            top: 600,
            right: 0,
            collapsible:false,
            minimizable:false,
            maximizable:false,
            onClose:close
        });

        function close(){
            _messenger = null;
        }
    }
    _messenger.html(_html);
}