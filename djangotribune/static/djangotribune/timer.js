/*
/ Registre et méthodes des timers utilisés
*/
refreshTimer = {
    timers : {},
    
    /*
    / Retourne un timer du registre
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
    / Stop un timer du registre
    */
    stopTimer : function(key) {
        var timerObj = this.getTimer( key );
        if (timerObj != null) {
            if(DEBUG) console.log("Timer Object:"+key+" => clearInterval()");
            clearInterval(timerObj);
            this.timers[key] = null;
        }
    },
    
    /*
    / Créé/édite un timer dans le registre
    */
    setTimer : function(key, funcString, milliseconds, force_zero) {
        if( typeof(milliseconds) != "number" ) milliseconds = parseInt(milliseconds);
        // Si la valeure égale zéro, par défaut on prends ça comme un stop du 
        // timer, on peut forcer l'utilisation du zéro avec l'option force_zero
        if(force_zero || milliseconds > 0) {
            if(DEBUG) console.log("Timer Object:"+key+" => setTimeout('"+funcString+"', "+milliseconds+")");
            this.timers[key] = setTimeout(funcString, milliseconds);
        } else {
            this.stopTimer(key);
        }
    }
};
