( function()
{
// from http://davidwalsh.name/function-debounce
Function.implement({
	debounce: function(wait, immediate) {
		var timeout,
		    func = this;
		return function() {
			var context = this, args = arguments;
			var later = function() {
				timeout = null;
				if (!immediate) func.apply(context, args);
			};
			var callNow = immediate && !timeout;
			clearTimeout(timeout);
			timeout = setTimeout(later, wait);
			if (callNow) func.apply(context, args);
		};
	}
});

}());
