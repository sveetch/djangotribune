/*
* The Django-tribune jQuery plugin
* 
* TODO: This lack of :
*       * Timer should be contained in plugin namespace or deprecated in favor of 
*         a jquery timer plugin;
*       * Correctly register clocks and compute clock indices;
*       * Display event (highlight, etc..);
*       * Themes usage, like codemirror with appending a css class with the theme 
*         slugname;
*       * Use qTip2 implement "out of screen clocks" and totoz display with qTip2 ?
*       * Option to use a view in modal window to edit custom settings;
*       * ???
* 
* NOTE: This is developed with thinking about channels. The multiple instances plugin 
*       possibility is respected so channels will be simply another djangotribune 
*       instances with different #id used as their unique key for timer.
*       When new channel is opened, the tribune interface should move on a tabbed 
*       display.
*       Core plugin must store all instance data in their element with elem.data().
*/
DEBUG = false; // TEMP

(function($){
    /*
     * Plugin extensions calling logic
     */
    $.fn.djangotribune = function(method) {
        if ( extensions[method] ) {
            return extensions[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof method === 'object' || ! method ) {
            return extensions.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  method + ' does not exist on jQuery.djangotribune' );
        }
    };

    /*
     * Plugin extension methods
     */
    var extensions = {
        /*
         * Initialize plugin, must be called first
         */
        init : function(options) {
            // Default for DjangoCodeMirror & CodeMirror
            var settings = $.extend( {
                "host" : '',
                "remote_path": '',
                "post_path": '',
                "clockfinder_path": '',
                "theme": 'default',
                "message_limit": 30,
                "refresh_active": true,
                "refresh_time_shifting": 10000,
                "urlopen_blank": true
            }, options);
            
            // Build DjangoTribune for each selected element
            return this.each(function() {
                var $this = $(this),
                    djangotribune_key = $this.attr('id')||'default',
                    djangotribune_scroll = $("<div class=\"djangotribune_scroll\"></div>").insertBefore("form", $this).append($("ul.messages", $this)),
                    input_checked = (settings.refresh_active) ? " checked=\"checked\"" : "",
                    refresh_active = $("<p class=\"refresh_active\"><label><input type=\"checkbox\" name=\"active\" value=\"1\"" +input_checked+ "/>Active refresh</label></p>").appendTo("form", $this);
                
                // Attach element's data
                $this.data("djangotribune", {
                    "djangotribune" : $this,
                    "key" : djangotribune_key,
                    "scroller" : djangotribune_scroll,
                    "settings": settings
                });
                $this.data("djangotribune_lastid", 0);
                
                // Default Ajax request settings
                $.ajaxSetup({
                    global: false,
                    type: "GET",
                    dataType: "json",
                    beforeSend: CSRFpass,
                    cache: false
                });
                
                // Bind djangotribune's specific events
                var extra_context = { "djangotribune": $this };
                $(window).bind("update_backend_display.djangotribune", events.update);
                $("input", refresh_active).change(extra_context, events.change_refresh_active);
                $("form input[type='submit']", $this).click(extra_context, events.submit);
                $("input.content_field", $this).keydown( extra_context, function(e){
                    if(e.keyCode == '13'){
                        e.stopPropagation();
                        return events.submit(e);
                    }
                    return true;
                });
                $("form", $this).bind("submit", function() { return false; });
                
                // First parsing from html
                $this.djangotribune('initial');
            });
        },
        
        /*
         * Parse HTML message list as initial backend, index/store their data and update 
         * the last_id
         */
        initial : function() {
            return this.each(function(){
                var $this = $(this),
                    data = $this.data("djangotribune"),
                    last_id = $this.data("djangotribune_lastid"),
                    currentid = 0;
                
                $(".djangotribune_scroll li.message", $this).each(function(index) {
                    currentid = parseInt( $("span.pk", this).html() );
                    
                    // Break to avoid doublet processing
                    if( last_id >= currentid  ) return false;
                                                                  
                    var identity_username = null;
                    if( $("span.identity", this).hasClass('username') ) {
                        identity_username = $("span.identity", this).html();
                    }
                    var data = {
                        "id": currentid,
                        "created": $("span.created", this).text(),
                        "clock": $("span.clock", this).text(),
                        "clock_indice": $("span.clock_indice", this).text(),
                        "clockclass": $("span.clockclass", this).text(),
                        "user_agent": $("span.identity", this).attr('title'),
                        "username": identity_username,
                        "web_render": $("span.content", this).html()
                    };
                    
                    // TODO: Put data in clock/timestamp/etc.. register and initialize 
                    //       events (clock, links, totoz, etc..) on rows
                    // ...
                });
                
                // First timer init
                if(data.settings.refresh_active){
                    // NOTE: To implement plugin multiple instances (like for each 
                    //       channel) there will be need of a specific timer's key 
                    //       naming (for each channel)
                    refreshTimer.setTimer(data.key, function(){ $this.djangotribune('refresh') }, data.settings.refresh_time_shifting)
                }
                
                // Push the last message id as reference for next backend requests
                $this.data("djangotribune_lastid", currentid);
            });
        },
        
        /*
         * Get the fucking backend
         */
        refresh : function(options) {
            return this.each(function(){
                var $this = $(this),
                    data = $this.data("djangotribune"),
                    last_id = $this.data("djangotribune_lastid"),
                    query = $.QueryString;
                    
                // Custom options if any
                options = options||{};
                
                // Check custom last_id
                if(options.last_id) {
                    last_id = options.last_id;
                }
                query.last_id = last_id;
                
                // Custom settings on the fly if any
                current_settings = data.settings;
                if(options.extra_settings){
                    current_settings = $.extend({}, current_settings, options.extra_settings);
                }
                
                // Perform request to fetch backend
                var url = CoreTools.get_request_url(current_settings.host, current_settings.remote_path, query);
                if(DEBUG) console.log("Djangotribune refresh on : "+url);
                $.ajax({
                    url: url,
                    data: {},
                    beforeSend: function(req){
                        $(".backend_loading", $this).show();
                    },
                    success: function (backend, textStatus) {
                        if(DEBUG) console.log("Djangotribune Request textStatus: "+textStatus);
                       
                        // Send signal to update messages list with the fetched backend 
                        // if there are at least one row
                        if(backend.length>0) {
                            $this.trigger("update_backend_display", [data, backend, last_id]);
                        }
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown){
                        if(DEBUG) console.log("Djangotribune Error request textStatus: "+textStatus);
                        if(DEBUG) console.log("Djangotribune Error request errorThrown: "+textStatus);
                       
                    },
                    complete: function (XMLHttpRequest, textStatus) {
                        $(".backend_loading", $this).hide();
                        // Relaunch timer
                        if(data.settings.refresh_active){
                            refreshTimer.setTimer(data.key, function(){ $this.djangotribune('refresh') }, data.settings.refresh_time_shifting)
                        }
                    }
                });
            });
        }
    };
    
    /*
     * Plugin event methods
     */
    var events = {
        /*
         * Update HTML to append new messages from the given backend data
         */
        update : function(event, data, backend, last_id, options) {
            var $this = $(event.target),
                current_message_length = $(".djangotribune_scroll li", $this).length;
            
            if(DEBUG) console.log("Djangotribune events.update");
 
            // Custom options if any
            options = options||{};
            current_settings = data.settings;
            if(options.extra_settings){
                current_settings = $.extend({}, current_settings, options.extra_settings);
            }
            
            var last_id = $this.data("djangotribune_lastid");
            
            $.each(backend, function(index, row) {
                // Drop the oldier message if message list has allready reached the 
                // message display limit
                if (current_message_length > 0 || current_message_length > data.settings.message_limit) {
                    $(".djangotribune_scroll li", $this).slice(0,1).remove();
                }
                
                // Compute some additionals row data
                row.css_classes = ["msg_clockclass_"+row.created.slice(8)+ClockIndicer.lpadding(row.clock_indice)];
                row.identity = {'title': row.user_agent, 'kind': 'anonymous', 'content': row.user_agent.slice(0,30)};
                if(row.author__username){
                    row.identity.kind = 'authenticated';
                    row.identity.content = row.author__username;
                }
                // Compile template, add its result to html and attach it his data
                $( templates.message_row(row) ).appendTo( $(".djangotribune_scroll ul", $this) ).data("djangotribune_row", row);
                
                // Update the "future" new last_id
                last_id = row.id;
            });
            
            // Push the last message id as reference for next backend requests
            $this.data("djangotribune_lastid", last_id);
        },

        /*
         * Change the settings "refresh_active" from the checkbox
         */
        change_refresh_active : function(event) {
            var $this = $(event.data.djangotribune),
                data = $this.data("djangotribune");
            
            if(DEBUG) console.log("Djangotribune events.change_refresh_active");
            
            if( $(this).attr("checked") ){
                // Enable refresh
                refreshTimer.setTimer(data.key, function(){ $this.djangotribune('refresh') }, data.settings.refresh_time_shifting)
                data.settings.refresh_active = true;
            } else {
                // Disable refresh
                refreshTimer.stopTimer(data.key);
                data.settings.refresh_active = false;
            }
            
            // Update settings
            $this.data("djangotribune", data);
        },

        /*
         * Submit form to post content
         */
        submit : function(event) {
            var $this = $(event.data.djangotribune),
                data = $this.data("djangotribune"),
                last_id = $this.data("djangotribune_lastid"),
                query = $.QueryString;
            
            if(DEBUG) console.log("Djangotribune events.submit");
 
            var content_value = $("input.content_field", $this).val();
            
            if(!content_value || content_value.length<1) return false;
            
            query.last_id = last_id;
            
            // Perform request to fetch backend
            var url = CoreTools.get_request_url(data.settings.host, data.settings.post_path, query);
            if(DEBUG) console.log("Djangotribune posting on : "+url);
            $.ajax({
                type: "POST",
                url: url,
                data: {"content": content_value},
                beforeSend: function(req){
                    // Stop timer and put display marks on content field input
                    refreshTimer.stopTimer(data.key);
                    $("form input[type='submit']", $this).attr("disabled", "disabled");
                    $("input.content_field", $this).addClass("disabled");
                    $(".backend_loading", $this).show();
                },
                success: function (backend, textStatus) {
                    if(DEBUG) console.log("Djangotribune Request textStatus: "+textStatus);
                   
                    $("input.content_field", $this).removeClass("error");
                    $("input.content_field", $this).val("");
                    
                    // Send signal to update messages list with the fetched backend 
                    // if there are at least one row
                    if(backend.length>0) {
                        $this.trigger("update_backend_display", [data, backend, last_id]);
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown){
                    if(DEBUG) console.log("Djangotribune Error request textStatus: "+textStatus);
                    if(DEBUG) console.log("Djangotribune Error request errorThrown: "+textStatus);
                   
                    $("input.content_field", $this).removeClass("disabled").addClass("error");
                },
                complete: function (XMLHttpRequest, textStatus) {
                    $("form input[type='submit']", $this).removeAttr("disabled");
                    $("input.content_field", $this).removeClass("disabled");
                    $(".backend_loading", $this).hide();
                    
                    // Relaunch timer
                    if(data.settings.refresh_active){
                        refreshTimer.setTimer(data.key, function(){ $this.djangotribune('refresh') }, data.settings.refresh_time_shifting)
                    }
                }
            });
            
            return false;
        }
    };
    
    var CoreTools = {
        /*
         * Return an exposant indice from the given number (padded on two digit)
         */
        get_request_url : function(host, path_view, options) {
            var url = host + path_view;
            if(options){
                url += "?" + $.param(options);
            }
            return url;
        }
    };
    
    var ClockIndicer = {
        // Exposant indices characters map
        indices : '¹²³⁴⁵⁶⁷⁸⁹',
        /*
         * Return an exposant indice from the given number (padded on two digit)
         */
        number_to_indice : function(number_i) {
            if( i > 1 )
                return ClockIndicer.indices[i-1];
            return '';
        },
        
        /*
         * Return a padded number on two digit from the given exposant indice
         */
        indice_to_number : function(indice) {
            var i = ClockIndicer.indices.indexOf(indice);
            // Cherche un indice sous forme d'exposant
            if( i > -1 )
                return ClockIndicer.lpadding(i+1);
            return '01';
        },
        
        /*
         * Format to a padded number on two digits
         */
        lpadding : function(indice) {
            if(indice > 0 && indice < 10) {
                return '0'+indice;
            }
            return "01";
        }
    };
    
    /*
     * Plugin HTML templates
     */
    var templates = {
        /*
         * Message row template
         * @content is an object with all needed variables by template
         */
        message_row: function(content) {
            // Display clock indice only if greater than 1
            var clock_indice = "&nbsp;&nbsp;";
            if(content.clock_indice > 1) {
                clock_indice = "<sup>"+ ClockIndicer.indices[content.clock_indice-1] +"</sup>";
            }
            var css_classes = content.css_classes||[];
            return "<li class=\"message "+ css_classes.join(" ") +"\">" +
                "<span class=\"clock\">"+ content.clock+clock_indice +"</span> " + 
                "<strong><span class=\"identity "+ content.identity.kind +"\" title=\""+ content.identity.title +"\">"+ content.identity.content +"</span></strong> " + 
                "<span class=\"content\">"+ content.web_render +"</span>" + 
            "</li>";
        }
    };
    
})( jQuery );