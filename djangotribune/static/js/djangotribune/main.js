/*
* The Django-tribune jQuery plugin
* 
* TODO: This lack of :
*       * Finalize all clock features;
*       * Use the header "X-Post-Id" to retrieve owned message posted and enable owner 
*         mark for anonymous;
*       * "clock_store" cleaning when dropping messages from the list
*       * User settings panel;
*       * Themes usage, like codemirror with appending a css class with the theme 
*         slugname;
*/
DEBUG = false; // To enable/disable message logs with "console.log()"

// Array Remove - By John Resig (MIT Licensed)
Array.prototype.remove = function(from, to) {
    var rest = this.slice((to || from) + 1 || this.length);
    this.length = from < 0 ? this.length + from : from;
    return this.push.apply(this, rest);
};

/*
 * Extend jQuery with a new method to insert text in an input at current cursor position
 * 
 * Stealed from :
 * 
 * http://stackoverflow.com/questions/946534/insert-text-into-textarea-with-jquery
 * 
 * Usage :
 * 
 *     $("input.myinput").insertAtCaret("My text");
 */
jQuery.fn.extend({
    insertAtCaret: function(myValue){
        return this.each(function(i) {
            if (document.selection) {
                //For browsers like Internet Explorer
                this.focus();
                var sel = document.selection.createRange();
                sel.text = myValue;
                this.focus();
            }
            else if (this.selectionStart || this.selectionStart == '0') {
                //For browsers like Firefox and Webkit based
                var startPos = this.selectionStart,
                    endPos = this.selectionEnd,
                    scrollTop = this.scrollTop;
                this.value = this.value.substring(0, startPos)+myValue+this.value.substring(endPos,this.value.length);
                this.focus();
                this.selectionStart = startPos + myValue.length;
                this.selectionEnd = startPos + myValue.length;
                this.scrollTop = scrollTop;
            } else {
                this.value += myValue;
                this.focus();
            }
        });
    }
});

/* 
 * The djangotribune plugin
 * 
 * Usage for first init :
 * 
 *     $(".mycontainer").djangotribune({options...});
 */
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
     * Timer methods and registries
     */
    var Timer = {
        timers : {},
        /*
        * Get the timer from registry
        */
        getTimer : function(key) {
            var timerObj;
            try {
                timerObj = this.timers[key];
            } catch (e) {
                timerObj = null;
            }
            return timerObj;
        },
        /*
        * Stop timer
        */
        stopTimer : function(key) {
            var timerObj = this.getTimer(key);
            if (timerObj !== null) {
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
    
    

    /*
     * Plugin extension methods
     */
    var extensions = {
        /*
         * Expose some debug infos
         */
        debug : function() {
            return this.each(function(){
                var $this = $(this),
                    data = $this.data("djangotribune"),
                    key = data.key;
                    
                console.log("'clock store' debug output");
                console.log( "@@ _index_ids @@" );
                console.log( clock_store._index_ids[key] );
                console.log( "@@ _index_timestamps @@" );
                console.log( clock_store._index_timestamps[key] );
                console.log( "@@ _index_dates @@" );
                console.log( clock_store._index_dates[key] );
                console.log( "@@ _index_clocks @@" );
                console.log( clock_store._index_clocks[key] );
                console.log( "@@ _count_timestamp @@" );
                console.log( clock_store._count_timestamp[key] );
                console.log( "@@ _count_short_clock @@" );
                console.log( clock_store._count_short_clock[key] );
                console.log( "@@ _index_user_ids @@" );
                console.log( clock_store._index_user_ids[key] );
                console.log( "@@ _index_user_timestamps @@" );
                console.log( clock_store._index_user_timestamps[key] );
                console.log( "@@ _index_user_clocks @@" );
                console.log( clock_store._index_user_clocks[key] );
                console.log( "@@ _map_clock @@" );
                console.log( clock_store._map_clock[key] );
                console.log( "@@ _map_clockids @@" );
                console.log( clock_store._map_clockids[key] );
            });
        },
        
        /*
         * Initialize plugin, must be called first
         */
        init : function(options) {
            // Default for DjangoCodeMirror & CodeMirror
            var settings = $.extend( {
                "host" : '',
                "remote_path": '',
                "post_path": '',
                "channel": null,
                "clockfinder_path": '',
                "theme": 'default',
                "message_limit": 30,
                "refresh_active": true,
                "refresh_time_shifting": 10000,
                "authenticated_username": null,
                "urlopen_blank": true
            }, options);
            
            // Build DjangoTribune for each selected element
            return this.each(function() {
                var $this = $(this),
                    djangotribune_key = "djangotribune-id-" + (settings.channel||'default'), // djangotribune instance ID, must be unique, reference to the current channel if any
                    djangotribune_scroll = $("<div class=\"djangotribune_scroll\"></div>").insertBefore("form", $this).append($("ul.messages", $this)),
                    refresh_input = templates.refresh_checkbox(settings).insertBefore("form .input-column .ctrlHolder", $this),
                    refresh_spinner = $('<i class="icon-refresh icon-spin within-input backend-refresh-spinner"></i>').insertBefore("form input.submit", $this).hide(),
                    refresh_error = $('<i class="icon-warning-sign within-input backend-refresh-error"></i>').insertBefore("form input.submit", $this).hide(),
                    absolute_container = $('<div class="absolute-message-container"><div class="content"></div></div>').css({"display": "none"}).appendTo("body"),
                    extra_context = {};
                
                // Attach element's data
                $this.data("djangotribune", {
                    "djangotribune": $this,
                    "key": djangotribune_key,
                    "scroller": djangotribune_scroll,
                    "refresh_spinner": refresh_spinner,
                    "refresh_error": refresh_error,
                    "absolute_container": absolute_container,
                    "settings": settings
                });
                $this.data("djangotribune_lastid", 0);
                
                // Open a new store for the current channel or default channel
                clock_store.new_store(djangotribune_key);
                
                // Default Ajax request settings
                $.ajaxSetup({
                    global: false,
                    type: "GET",
                    dataType: "json",
                    beforeSend: CSRFpass,
                    ifModified: true,
                    cache: false
                });
                
                // Bind djangotribune's specific events
                extra_context.djangotribune = $this;
                $(window).bind("update_backend_display.djangotribune", events.update);
                $("input", refresh_input).change(extra_context, events.change_refresh_active);
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
                    currentid = 0,
                    owned;
                
                $(".djangotribune_scroll li.message", $this).each(function(index) {
                    currentid = parseInt( $(this).attr("data-tribune-pk") );
                    
                    // Break to avoid doublet processing
                    if( last_id >= currentid  ) return false;
                    
                    // Chech message author identity
                    var identity_username = null;
                    if( $("span.identity", this).hasClass('username') ) {
                        identity_username = $("span.identity", this).html();
                    }
                    // Compile message datas as a message object
                    var message_data = {
                        "id": currentid,
                        "created": $(this).attr("data-tribune-created"),
                        "clock": $("span.clock", this).text(),
                        "clock_indice": parseInt( $(this).attr("data-tribune-clock_indice") ),
                        "clockclass": $(this).attr("data-tribune-clockclass"),
                        "user_agent": $("span.identity", this).attr('title'),
                        "author__username": identity_username,
                        "owned": ($(this).attr("data-tribune-owned") && $(this).attr("data-tribune-owned")=="true") ? true : false,
                        "web_render": $("span.content", this).html()
                    };
            
                    // Store the clock
                    clock_store.add(data.key, message_data.created, message_data.clock_indice, message_data.owned);
                    
                    // Put data in clock/timestamp/etc.. register and initialize 
                    // events (clock, links, totoz, etc..) on rows
                    events.bind_message($this, data, this, message_data, true);
                });
                
                // First timer init
                if(data.settings.refresh_active){
                    Timer.setTimer(data.key, function(){ $this.djangotribune('refresh'); }, data.settings.refresh_time_shifting);
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
                    query = $.QueryString,
                    refresh_spinner = data.refresh_spinner,
                    refresh_error = data.refresh_error;
                    
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
                        refresh_spinner.show();
                    },
                    success: function (backend, textStatus) {
                        if(DEBUG) console.log("Djangotribune Request textStatus: "+textStatus);
                        refresh_error.hide();
                        
                        if(textStatus == "notmodified") return false;
                        
                        // Send signal to update messages list with the fetched backend 
                        // if there are at least one row
                        if(backend.length>0) {
                            $this.trigger("update_backend_display", [data, backend, last_id]);
                        }
                    },
                    error: function(XMLHttpRequest, textStatus, errorThrown){
                        if(DEBUG) console.log("Djangotribune Error request textStatus: "+textStatus);
                        if(DEBUG) console.log("Djangotribune Error request errorThrown: "+textStatus);
                        refresh_error.show();
                    },
                    complete: function (XMLHttpRequest, textStatus) {
                        refresh_spinner.hide();
                        // Relaunch timer
                        if(data.settings.refresh_active){
                            Timer.setTimer(data.key, function(){ $this.djangotribune('refresh'); }, data.settings.refresh_time_shifting);
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
         * This should not be used if there are no message in backend
         */
        update : function(event, data, backend, last_id, options) {
            var element,
                element_ts,
                owned,
                $this = $(event.target),
                current_message_length = $(".djangotribune_scroll li", $this).length;
            
            if(DEBUG) console.log("Djangotribune events.update");
 
            // Drop the notice for empty lists
            $(".djangotribune_scroll li.notice.empty", $this).remove();
 
            // Custom options if any
            options = options||{};
            current_settings = data.settings;
            if(options.extra_settings){
                current_settings = $.extend({}, current_settings, options.extra_settings);
            }
            // Get the current knowed last post ID
            last_id = $this.data("djangotribune_lastid");
            
            $.each(backend, function(index, row) {
                // Drop the oldiest item if message list has allready reached the 
                // display limit
                // TODO: This should drop also item clocks references from the 
                // "clock_store"
                if (current_message_length >= data.settings.message_limit) {
                    $(".djangotribune_scroll li", $this).slice(0,1).remove();
                }
            
                // Register the message in the clock store
                element_ts = clock_store.add(data.key, row.created, null, row.owned);
                // Update clock attributes from computed values by the clock store
                row.clock_indice = element_ts.indice;
                row.clockclass = clock_store.clock_to_cssname(element_ts.clock);
                
                // Compute some additionals row data
                row.css_classes = ["msgclock_"+row.clockclass];
                if(row.owned) row.css_classes.push("owned");
                row.identity = {'title': row.user_agent, 'kind': 'anonymous', 'content': row.user_agent.slice(0,30)};
                row.owned = owned;
                if(row.author__username){
                    row.identity.kind = 'authenticated';
                    row.identity.content = row.author__username;
                }
                // Compile template, add its result to html and attach it his data
                element = $( templates.message_row(row) ).appendTo( $(".djangotribune_scroll ul", $this) ).data("djangotribune_row", row);
                // Bind all related message events
                events.bind_message($this, data, element, row);
                
                // Update to the new last_id
                last_id = row.id;
            });
            
            // Push the last message id as reference for next backend requests
            $this.data("djangotribune_lastid", last_id);
        },

        /*
         * Change the settings "refresh_active" from the checkbox
         * TODO: This should be memorized in a cookie or something else more persistent 
         * (like user personnal settings) than a page instance
         */
        change_refresh_active : function(event) {
            var $this = $(event.data.djangotribune),
                data = $this.data("djangotribune");
            
            if(DEBUG) console.log("Djangotribune events.change_refresh_active");
            
            if( $(this).attr("checked") ){
                // Enable refresh
                Timer.setTimer(data.key, function(){ $this.djangotribune('refresh'); }, data.settings.refresh_time_shifting);
                data.settings.refresh_active = true;
            } else {
                // Disable refresh
                Timer.stopTimer(data.key);
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
                refresh_spinner = data.refresh_spinner,
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
                    Timer.stopTimer(data.key);
                    $("form input[type='submit']", $this).attr("disabled", "disabled");
                    $("input.content_field", $this).addClass("disabled");
                    refresh_spinner.show();
                },
                success: function (backend, textStatus) {
                    if(DEBUG) console.log("Djangotribune Request textStatus: "+textStatus);
                   
                    $("input.content_field", $this).removeClass("error");
                    $("input.content_field", $this).val("");
                        
                    if(textStatus == "notmodified") return false;
                    
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
                    refresh_spinner.hide();
                    
                    // Relaunch timer
                    if(data.settings.refresh_active){
                        Timer.setTimer(data.key, function(){ $this.djangotribune('refresh'); }, data.settings.refresh_time_shifting);
                    }
                }
            });
            
            return false;
        },

        /*
         * Bind message events and add some sugar on message HTML
         * 
         * TODO: * much "DRY"
         *       * bubble display for items out of screen
         */
        bind_message : function(djangotribune_element, djangotribune_data, message_element, message_data, initial) {
            var preload,
                clock,
                pointer_name,
                clock_name,
                css_attrs,
                initial = (initial) ? true : false;
            
            // TODO: move in the djangotribune data
            // NOTE: initial HTML use entity reference and JSON backend use decimal 
            // reference, so for now we need to support both of them
            var regex_cast_initial = new RegExp(djangotribune_data.settings.authenticated_username+"&#60;");
            var regex_cast_backend = new RegExp(djangotribune_data.settings.authenticated_username+"&lt;");
            
            // Add event to force URL opening in a new window
            $("span.content a", message_element).click( function() {
                window.open($(this).attr("href"));
                return false;
            });

            // Smiley images
            $("span.content a.smiley", message_element).each(function(index) {
                preload = new Image();
                preload.src = $(this).attr("href");
            }).mouseenter(
                {"djangotribune": djangotribune_element}, events.display_smiley
            ).mouseleave( function() {
                $("p.smiley_container", djangotribune_element).remove();
            });
            
            // Add flat clock as a class name on pointers
            $("span.content span.pointer", message_element).each(function(index) {
                $(this).addClass("pointer_"+clock_store.plainclock_to_cssname($(this).text()));
            });
            
            // Broadcasting
            if( message_data.web_render.toLowerCase().search(/moules&lt;/) != -1 || message_data.web_render.toLowerCase().search(/moules&#60;/) != -1 ){
                // Global mussles broadcasting
                $(message_element).addClass("musslecast");
                $('span.marker', message_element).html("<i class=\"icon-asterisk\"></i>")
            } else if ( djangotribune_data.settings.authenticated_username && ( message_data.web_render.toLowerCase().search( regex_cast_initial ) != -1 || message_data.web_render.toLowerCase().search( regex_cast_backend ) != -1 ) ){
                // User broadcasting
                $(message_element).addClass("usercast");
                $('span.marker', message_element).html("<i class=\"icon-asterisk\"></i>")
            }
                
            // Message reference clock
            $("span.clock", message_element).mouseenter(function(){
                // Get related pointers in all messages and highlight them
                $(this).parent().addClass("highlighted");
                pointer_name = "pointer_"+clock_store.plainclock_to_cssname(jQuery.trim($(this).text()));
                $("li.message span.pointer."+pointer_name, djangotribune_element).each(function(index) {
                    $(this).addClass("highlighted");
                    $(this).parent().parent().addClass("highlighted");
                });
            }).mouseleave(function(){
                // Get related pointers and un-highlight them
                $(this).parent().removeClass("highlighted");
                pointer_name = "pointer_"+clock_store.plainclock_to_cssname(jQuery.trim($(this).text()));
                $("li.message span.pointer."+pointer_name, djangotribune_element).each(function(index) {
                    $(this).removeClass("highlighted");
                    $(this).parent().parent().removeClass("highlighted");
                });
            }).click(function(){
                // Focus in input and add the clock to answer it
                clock = jQuery.trim($(this).text());
                $("#id_content").insertAtCaret(clock+" ");
            });
            
            // Clock pointers contained
            $("span.content span.pointer", message_element).mouseenter(function(){
                var $this_pointer = $(this),
                    clock_pointer = jQuery.trim($this_pointer.text());
                $this_pointer.addClass("highlighted");
                
                // Get related pointers in all messages and highlight them
                pointer_name = "pointer_"+clock_store.plainclock_to_cssname(clock_pointer);
                $("li.message span.pointer."+pointer_name, djangotribune_element).each(function(index) {
                    $(this).addClass("highlighted");
                });
                
                // Get related messages and highlight them
                clock_name = "msgclock_"+clock_store.plainclock_to_cssname(clock_pointer);
                $("li."+clock_name, djangotribune_element).each(function(index) {
                    $(this).addClass("highlighted");
                    if(DEBUG) {
                        console.group("Pointer event for message: %s", clock_pointer)
                        console.log("Window scrollTop: "+ $(window).scrollTop());
                        console.log("Pointer offset: "+ $this_pointer.offset().top);
                        console.log("Reference offset from pointer: "+ $(this).offset().top);
                    }
                    // Display messages that are out of screen
                    if($(window).scrollTop() > $(this).offset().top) {
                        // Append html now so we can know about his future height
                        djangotribune_data.absolute_container.html( $(this).html() );
                        css_attrs = { "left":djangotribune_data.scroller.offset().left };
                        // Calculate the coordinates of the bottom container displayed 
                        // at top by default
                        var container_bottom_position = $(window).scrollTop() + djangotribune_data.absolute_container.outerHeight(true);
                        
                        // Display at top of the screen by default
                        if( $this_pointer.offset().top > container_bottom_position) {
                            css_attrs.top = 0;
                            css_attrs.bottom = "";
                            djangotribune_data.absolute_container.removeClass("at-bottom").addClass("at-top");
                            if(DEBUG) console.info("Absolute display at top");
                        // Display at bottom of the screen
                        } else {
                            css_attrs.top = "";
                            css_attrs.bottom = 0;
                            djangotribune_data.absolute_container.removeClass("at-top").addClass("at-bottom");
                            if(DEBUG) console.info("Absolute display at bottom");
                        }
                        // Apply css position and show it
                        djangotribune_data.absolute_container.css(css_attrs).show()
                    }
                    if(DEBUG) console.groupEnd();
                });
            }).mouseleave(function(){
                $(this).removeClass("highlighted");
                // Get related pointers and un-highlight them
                pointer_name = "pointer_"+clock_store.plainclock_to_cssname(jQuery.trim($(this).text()));
                $("li.message span.pointer."+pointer_name, djangotribune_element).each(function(index) {
                    $(this).removeClass("highlighted");
                });
                // Get related messages and un-highlight them
                clock_name = "msgclock_"+clock_store.plainclock_to_cssname(jQuery.trim($(this).text()));
                $("li."+clock_name, djangotribune_element).each(function(index) {
                    $(this).removeClass("highlighted");
                });
                
                // Allways empty the absolute display container
                djangotribune_data.absolute_container.html("").hide()
            });
            
            // Mark answers to current user messages
            // TODO: this use "simple" clocks as references without checking, so this 
            //       will also mark same clock from another day if they are somes in 
            //       history
            if (djangotribune_data.settings.authenticated_username){
                $("span.content span.pointer", message_element).each( function(i){
                    if( clock_store.is_user_clock(djangotribune_data.key, $(this).text()) ) {
                        $(this).addClass("pointer-answer").parent().parent().addClass("answer").find('span.marker').html("<i class=\"icon-comment\"></i>");
                    }
                });
            }
        },
        /*
         * Display the smiley in a "bubble tip" positionned from the element
         */
        display_smiley : function(event) {
            var $this = $(event.target),
                djangotribune_element = event.data.djangotribune,
                url = $this.attr("href"),
                alt = ($this.attr("alt")||''),
                margin = 25,
                top_pos = ($this.offset().top + margin),
                left_pos = ($this.offset().left + margin);
            // Remove all previous smiley if any
            $("p.smiley_container", djangotribune_element).remove();
            // Build container positionned at the bottom of the element source
            var container = $("<p class=\"smiley_container\"><img src=\""+ url +"\" alt=\""+ (alt||'') +"\"/>"+"</p>").css({
                "height": "",
                "position":"absolute",
                "padding":"0",
                "top": top_pos+"px",
                "bottom": "",
                "left": left_pos+"px"
            }).prependTo(djangotribune_element);
            
            // By default the image is positionned at the bottom of the element, but 
            // if its bottom corner is "out of screen", we move it at the top of element.
            var bottom_screen_pos = $(document).scrollTop() + $(window).height(),
                image_height = container.height(),
                bottom_image_pos = top_pos + image_height;
            if(bottom_image_pos > bottom_screen_pos) {
                top_pos = top_pos-image_height-(margin+10);
                container.css("height", image_height+"px").css("top", top_pos).css("bottom", "");
            }
        }
    };
    
    

    /*
     * Clock date store
     * 
     * Should know about any clock/timestamp with some facilities to get various format, 
     * append new item, remove them(?) and an minimal interface to search on items
     * 
     * Items ID are internal timestamps, this is a concat of the date, the time and the indice like that :
     * 
     *  YYYYMMDD+hhmmss+i
     * 
     */
    var clock_store = {
        _indices : '¹²³⁴⁵⁶⁷⁸⁹', // Exposant indices characters map
 
        _index_keys : [], // registry keys, each key store his own stuff, values between key stores are never related
        _index_ids : {}, // IDs are internal timestamp 
        _index_timestamps : {}, // timestamp that represents clocks in a full date format
        _index_dates : {}, // dates, NOTE: should be removed
        _index_clocks : {}, // clocks
        _index_user_ids : {}, // ids owned by the current user
        _index_user_timestamps : {}, // timestamps owned by the current user
        _index_user_clocks : {}, // clocks owned by the current user
 
        _map_clock : {}, // a map indexed on clocks, with all their timestamps as values, each clock can have multiple timestamp
        _map_clockids : {}, // a map indexed on clocks, with all their ids as values, each clock can have multiple ids
 
        _count_timestamp : {}, // Timestamps count
        _count_short_clock : {}, // Short clock count
 
        /*
        * New registry initialization
        */
        'new_store' : function(key) {
            this._index_keys.push(key);
            this._index_ids[key] = [];
            this._index_timestamps[key] = [];
            this._index_dates[key] = [];
            this._index_clocks[key] = [];
            this._index_user_ids[key] = [];
            this._index_user_timestamps[key] = [];
            this._index_user_clocks[key] = [];
            
            this._map_clock[key] = {};
            this._map_clockids[key] = {};
            
            this._count_timestamp[key] = {};
            this._count_short_clock[key] = {};
        },
        
        /*
        * Add a timestamp entry to a key store
        * 
        * NOTE: Shouldn't be an "id" as argument instead of a "timestamp" ??
        */
        'add' : function(key, timestamp, indice, user_owned) {
            var indice = (indice) ? indice : this.get_timestamp_indice(key, timestamp),
                id = timestamp+this.lpadding(indice),
                clock = this.timestamp_to_full_clock(timestamp, indice),
                short_clock = this.timestamp_to_short_clock(timestamp),
                date = this.timestamp_to_date(timestamp);
            
            //console.log("ADDING= key:"+key+"; timestamp:"+timestamp+"; indice:"+indice+"; user_owned:"+user_owned+";");
            
            // Indexing EVERYTHING !
            if(this._index_dates[key].indexOf(date) == -1) this._index_dates[key].push(date);
            
            if(this._index_ids[key].indexOf(id) == -1) this._index_ids[key].push(id);
            
            if(this._index_timestamps[key].indexOf(timestamp) == -1) this._index_timestamps[key].push(timestamp);
 
            if(this._index_clocks[key].indexOf(clock) == -1) this._index_clocks[key].push(clock);
            if(this._index_clocks[key].indexOf(short_clock) == -1) this._index_clocks[key].push(short_clock);
            
            // Count TIMESTAMP=>COUNT
            if(!this._count_timestamp[key][timestamp]) this._count_timestamp[key][timestamp] = 0; // if array doesnt allready exist, create it
            this._count_timestamp[key][timestamp] += 1;
            
            // Count SHORT_CLOCK=>COUNT
            if(!this._count_short_clock[key][short_clock]) this._count_short_clock[key][short_clock] = 0; // if array doesnt allready exist, create it
            this._count_short_clock[key][short_clock] += 1;
            
            // Map CLOCK=>[TIMESTAMP,..] and SHORT_CLOCK=>[TIMESTAMP,..]
            if(!this._map_clock[key][clock]) this._map_clock[key][clock] = []; // if array doesnt allready exist, create it
            if(this._map_clock[key][clock].indexOf(timestamp) == -1) this._map_clock[key][clock].push(timestamp);
            if(!this._map_clock[key][short_clock]) this._map_clock[key][short_clock] = []; // if array doesnt allready exist, create it
            if(this._map_clock[key][short_clock].indexOf(timestamp) == -1) this._map_clock[key][short_clock].push(timestamp);
            
            // Map CLOCK=>[ID,..] and SHORT_CLOCK=>[ID,..]
            if(!this._map_clockids[key][clock]) this._map_clockids[key][clock] = []; // if array doesnt allready exist, create it
            if(this._map_clockids[key][clock].indexOf(id) == -1) this._map_clockids[key][clock].push(id);
            if(!this._map_clockids[key][short_clock]) this._map_clockids[key][short_clock] = []; // if array doesnt allready exist, create it
            if(this._map_clockids[key][short_clock].indexOf(id) == -1) this._map_clockids[key][short_clock].push(id);
            
            // Flag as a owned clock if true
            if(user_owned){ 
                if(this._index_user_ids[key].indexOf(id) == -1 ) this._index_user_ids[key].push(id);
                if(this._index_user_timestamps[key].indexOf(timestamp) == -1 ) this._index_user_timestamps[key].push(timestamp);
                if(this._index_user_clocks[key].indexOf(clock) == -1 ) this._index_user_clocks[key].push(clock);
            }
            
            return {'id':id, 'timestamp':timestamp, 'date':date, 'clock':clock, 'indice':indice, 'short_clock':short_clock};
        },
 
        /*
        * Remove a timestamp entry from a key store
        * 
        * NOTE: Shouldn't be an "id" as argument instead of a "timestamp" and "indice" ??
        */
        'remove' : function(key, timestamp, indice) {
            // TODO: full clean of given timestamp in indexes and map
            //       Needed to clear history to avoid too much memory usage when user stay a long time
            //       This is not finished, but not used also for now, we need before to 
            //       see what index/count/map is really useful
            var id = timestamp+this.lpadding(indice),
                clock = this.timestamp_to_full_clock(timestamp, indice),
                short_clock = this.timestamp_to_short_clock(timestamp),
                date = this.timestamp_to_date(timestamp);
            
            delete this._index_ids[key][id];
            delete this._index_clocks[key][clock]; //full clock
            
            this._map_clock[key][clock].remove( this._map_clock[key].indexOf(clock) );
            this._map_clockids[key][clock].remove( this._map_clockids[key].indexOf(clock) );
            
            delete this._index_user_ids[key][id];
            delete this._index_user_clocks[key][clock]; //full clock
            
            this._count_timestamp[key][timestamp] -= 1;
            this._count_short_clock[key][timestamp] -= 1;
            
            return {'id':id, 'timestamp':timestamp, 'date':date, 'clock':clock, 'indice':indice, 'short_clock':short_clock};
        },
 
        // Calculate in "real time" the indice for the given timestamp using indexes
        get_timestamp_indice : function(key, ts) {
            if(!this._count_timestamp[key][ts]) {
                return 1;
            }
            // Identical timestamp count incremented by one
            return this._count_timestamp[key][ts]+1;
        },
        // Check if a clock is owned by the current user
        // Attempt a "simple" clock in argument, not a "full" clock
        is_user_clock : function(key, clock) {
            clock = this.clock_to_full_clock(clock);
            return (this._index_user_clocks[key].indexOf(clock) > -1 );
        },
 
 
        /* ********** PUBLIC STATICS ********** */
        /*
         * timestamp: 20130124005502
         * id: 2013012400550201 (the two last digits are the indice)
         * clock: 00:55:02 or 00:55 or 00:55:02²
         * clockclass: 005502
         * full clock: 00:55:02:01 (':01' is the indice padded on 2 digits)
         * short clock: 00:55 (seconds are stripped)
         */
        id_to_full_clock : function(id) {
            return this.timestamp_to_clock(id)+":"+id.substr(14,2);
        },
 
        timestamp_to_full_clock : function(ts, i) {
            return this.timestamp_to_clock(ts)+":"+this.lpadding(i);
        },
        timestamp_to_clock : function(ts) {
            return ts.substr(8,2)+":"+ts.substr(10,2)+":"+ts.substr(12,2);
        },
        timestamp_to_short_clock : function(ts) {
            return ts.substr(8,2)+":"+ts.substr(10,2);
        },
        // Renvoi un nom de classe composé d'une horloge sans les : à partir d'un timestamp
        timestamp_to_clockclass : function(ts) {
            return ts.substr(8,6);
        },
        // Renvoi la partie du timestamp concernant la date, sans l'horloge et le reste
        timestamp_to_date : function(ts) {
            return this.split_timestamp(ts)[0];
        },
        // Sépare en deux parties : date et time
        split_timestamp : function(ts) {
            return [ts.substr(0,8), ts.substr(8)];
        },
 
        // Convert a clock HH:MM[:SS[i]] to a full clock
        clock_to_full_clock : function(clock) {
            if(clock.length > 8) {
                return clock.substr(0,8)+":"+this.indice_to_number(clock.substr(8,2));
            } else if(clock.length < 8) {
                // short clock is assumed to be at second 00
                return clock+":00:01";
            }
            return clock+":01";
        },
 
        // Format to a padded number on two digits
        lpadding : function(indice) {
            if(indice > 0 && indice < 10) {
                return '0'+indice;
            }
            return "01";
        },
 
        // Return an exposant indice from the given number (padded on two digit)
        number_to_indice : function(i) {
            if( i > 1 )
                return this._indices[i-1];
            return '';
        },
        // Return a padded number on two digit from the given exposant indice
        indice_to_number : function(indice) {
            var i = this._indices.indexOf(indice);
            // Cherche un indice sous forme d'exposant
            if( i > -1 )
                return this.lpadding(i+1);
            return '01';
        },
        // Parse a plain clock "HH:MM[:SS[i]]" and return a "flat" version (without the ":") 
        // suitable for class/id css name
        // If not present in clock, default indice is "01"
        plainclock_to_cssname : function(clock) {
            var indice = "01";
            if(clock.length > 8){
                indice = this.indice_to_number(clock.substr(8,2));
                clock = clock.substr(0,8);
            }
            return clock.split(":").join("")+indice;
        },
        // Convert a full clock "HH:MM[:SS:[ii]]" to a "flat" version (without the ":") 
        // suitable for class/id css name
        clock_to_cssname : function(clock) {
            return clock.split(":").join("");
        }
    };
    
    
    
    /*
     * Various utilities
     */
    var CoreTools = {
        /*
         * Build and return a full url from the given args
         */
        get_request_url : function(host, path_view, options) {
            var url = host + path_view;
            if(options){
                url += "?" + $.param(options);
            }
            return url;
        }
    };
    
    
    
    /*
     * Plugin HTML templates
     * This is not "real" templates as we can see it with some library like "Mustach.js" 
     * and others
     */
    var templates = {
        /*
         * Message row template
         * @content is an object with all needed attributes for the template
         */
        refresh_checkbox: function(settings) {
            var input_checked = (settings.refresh_active) ? " checked=\"checked\"" : "";
 
            //return $('<p class="refresh_active"><label><input type="checkbox" name="active" value="1"'+ input_checked +'/>Active refresh</label></p>');
            return $('<p class="refresh_active"><input type="checkbox" name="active" value="1"'+ input_checked +'/></p>');
        },
 
        /*
         * Message row template
         * @content is an object with all needed attributes for the template
         */
        message_row: function(content) {
            var clock_indice = "&nbsp;",
                css_classes = content.css_classes||[];
            // Display clock indice only if greater than 1
            if(content.clock_indice > 1) clock_indice = clock_store.number_to_indice(content.clock_indice);
 
            return "<li class=\"message "+ css_classes.join(" ") +"\"><span class=\"marker\"></span>" +
                "<span class=\"clock\">"+ content.clock+"<sup>"+clock_indice +"</sup></span> " + 
                "<strong><span class=\"identity "+ content.identity.kind +"\" title=\""+ content.identity.title +"\">"+ content.identity.content +"</span></strong> " + 
                "<span class=\"content\">"+ content.web_render +"</span>" + 
            "</li>";
        }
    };
    
})( jQuery );