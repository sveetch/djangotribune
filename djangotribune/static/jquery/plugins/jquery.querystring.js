/*
 * Very simple plugin to parse request arguments
 * From http://stackoverflow.com/questions/901115/get-query-string-values-in-javascript
*/
(function($) {
    $.QueryString = (function() {
        var e,
            a = /\+/g,  // Regex for replacing addition symbol with a space
            r = /([^&=]+)=?([^&]*)/g,
            d = function (s) { return decodeURIComponent(s.replace(a, " ")); },
            q = window.location.search.substring(1),
            urlParams = {};

        while (e = r.exec(q)){
            urlParams[d(e[1])] = d(e[2]);
        }
        
        return urlParams;
    })(window.location.search.substr(1).split('&'))
})(jQuery);