/*
/ Timer methods
*/
refreshTimer = {
    timers : {},
    /*
     * Get the timer from registry
     */
    getTimer : function(key) {
        try {
            var timerObj = this.timers[key];
        } catch (e) {
            var timerObj = null;
        }
        return timerObj;
    },
    /*
     * Stop timer
     */
    stopTimer : function(key) {
        var timerObj = this.getTimer(key);
        if (timerObj != null) {
            if(DEBUG) console.log("Timer '"+key+"' cleared");
            clearInterval(timerObj);
            this.timers[key] = null;
        }
    },
    /*
     * Set a new timer
     */
    setTimer : function(key, funcString, milliseconds, force_zero) {
        if( typeof(milliseconds) != "number" ) milliseconds = parseInt(milliseconds);
        this.stopTimer(key); // Clear previous clearInterval from memory
        if(DEBUG) console.log("Timer '"+key+"' setted for "+milliseconds+" milliseconds");
        this.timers[key] = setTimeout(funcString, milliseconds);
    }
};