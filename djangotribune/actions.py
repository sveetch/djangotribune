# -*- coding: utf-8 -*-
"""
Message commands parser

Action idea to implement (or not)
=================================

Admin command to edit a post by clock selected on the last clock with this pattern so 
clock out of backend can be edited too : ::

    /admin edit clock 12:00:00

If the Ban on IP is implemented, an admin command to ban directly on IP : ::

    /admin ban ip XXX.XXX.XXX.XXX

Or ban on the ip used to post the message on the given clock : ::

    /admin ban clock 12:00:00

Flood tribune with some pre-registred message(s) : ::

    /admin flood FLOODNAME

"""
import datetime, urllib, urllib2, json
from base64 import b64encode

from django.conf import settings
from django.core.exceptions import ValidationError

from djangotribune.settings_local import (
    TRIBUNE_MESSAGES_UA_COOKIE_NAME, TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, 
    TRIBUNE_MESSAGES_UA_LENGTH_MIN, TRIBUNE_BAK_SESSION_NAME,
    TRIBUNE_LASTFM_API_URL, TRIBUNE_LASTFM_API_KEY
)
from djangotribune.models import FILTER_TARGET_CHOICE, FILTER_TARGET_ALIASES, FILTER_KIND_ALIASES
from djangotribune.bak import BakController

class ActionError(ValidationError):
    pass

class CommandBase(object):
    """Base command action"""
    required_args = 0
    need_to_push_data = False
    need_to_patch_response = False
    
    def __init__(self, args, author, cookies, session):
        self.args = args
        self.author = author
        self.cookies = cookies
        self.session = session
        
        self.opt_name = None
        if self.required_args and len(self.args):
            self.opt_name = self.args.pop(0)
    
    def validate(self):
        """
        Used by form to validate the command action, this should raise an 
        ``ActionError`` for any error
        """
        return True
    
    def execute(self):
        """Place to proceed to action processing"""
        pass
    
    def patch_response(self, response):
        """Used by views to patch the response"""
        return response
    
    def push_data(self, data):
        """Used by form to push data in a message to save"""
        return data

class CommandActionName(CommandBase):
    """
    Command action to save a custom name to replace the *user_agent*
    
    Name saving is made by a special cookie, so if the user lost or delete his cookie, 
    he lost his custom name.
    
    Add new ua : ::
        /name Plop
    
    Remove the saved ua : ::
        /name
    """
    need_to_patch_response = True
    
    def __init__(self, *args, **kwargs):
        super(CommandActionName, self).__init__(*args, **kwargs)
        self.new_name = None
        self.expires = datetime.datetime.strftime(datetime.datetime.utcnow() + datetime.timedelta(seconds=TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE), "%a, %d-%b-%Y %H:%M:%S GMT")
        
    def execute(self):
        if len(self.args)>0:
            self.__set_name()
    
    def __set_name(self):
        """
        Prepare the new name to use
        """
        self.new_name = " ".join(self.args).encode('utf-8')
        self.session['tribune_name'] = self.new_name
        
    def patch_response(self, response):
        """
        Patch response to set or update cookie
        """
        # Set the cookie to save the new name
        if self.new_name and len(self.new_name) >= TRIBUNE_MESSAGES_UA_LENGTH_MIN:
            response.set_cookie(TRIBUNE_MESSAGES_UA_COOKIE_NAME, b64encode(self.new_name), max_age=TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, expires=self.expires, domain=settings.SESSION_COOKIE_DOMAIN)
        # Delete the cookie to drop custom name
        else:
            response.set_cookie(TRIBUNE_MESSAGES_UA_COOKIE_NAME, '', max_age=TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, expires=self.expires, domain=settings.SESSION_COOKIE_DOMAIN)
            response.delete_cookie(TRIBUNE_MESSAGES_UA_COOKIE_NAME)
        
        return response

class CommandBak(CommandBase):
    """
    Command action to use message filtering
    
    To enable filters usage : ::

        /bak on

    To disable filters usage : ::

        /bak off
    
    To add a new filter (``add`` implying exact kind) : ::

        /bak add TARGET PATTERN
        /bak set TARGET KIND PATTERN

    To delete a registred filter (``del`` implying exact kind) : ::

        /bak del TARGET PATTERN
        /bak remove TARGET KIND PATTERN

    To save actual filters in session (only for registred users) : ::

        /bak save

    To load the save filters (only for registred users) : ::

        /bak load
    """
    required_args = 1
    option_names = ('on', 'off', 'add', 'set', 'del', 'remove', 'save', 'load', 'reset')
    short_options = ('on', 'off', 'save', 'load', 'reset') # options than didn't need arguments
    lv1_options = ('add', 'del') # options than require only one argument
    lv2_options = ('set', 'remove') # options than require only two argument
    
    def __init__(self, *args, **kwargs):
        super(CommandBak, self).__init__(*args, **kwargs)
        self.controller = None
        
        self.available_filter_targets = dict(FILTER_TARGET_ALIASES).keys()
        self.available_filter_kinds = dict(FILTER_KIND_ALIASES).keys()
        
    def validate(self):
        # Is an allowed option name
        if not self.opt_name:
            raise ActionError(u"This action require at least one argument.")
        if self.opt_name not in self.option_names:
            raise ActionError(u"Unkown option '{option}' in your command action.".format(option=self.opt_name))
        # Some options requires arguments
        # This is tricky but there are few option and not many different option needs
        if self.opt_name not in self.short_options:
            if self.opt_name in self.lv1_options:
                if len(self.args)<2:
                    raise ActionError(u"Option '{option}' require a target and a pattern.".format(option=self.opt_name))
                elif self.args[0] not in self.available_filter_targets:
                    raise ActionError(u"Target '{arg}' is not valid'.".format(arg=self.args[0]))
            elif self.opt_name in self.lv2_options:
                if len(self.args)<3:
                    raise ActionError(u"Option '{option}' require a target, a kind and a pattern.".format(option=self.opt_name))
                elif self.args[0] not in self.available_filter_targets:
                    raise ActionError(u"Target '{arg}' is not valid'.".format(arg=self.args[0]))
                elif self.args[1] not in self.available_filter_kinds:
                    raise ActionError(u"Kind '{arg}' is not valid'.".format(arg=self.args[1]))
            
        return True
    
    def execute(self):
        # Get the current controller in session if any, else initialize a empty 
        # controller
        self.controller = self.session.get(TRIBUNE_BAK_SESSION_NAME, BakController(self.author))
        
        do_method_name = 'do_{0}'.format(self.opt_name)
        if hasattr(self, do_method_name):
            getattr(self, do_method_name)()
            # Force saving session because controller changes is invisible to the 
            # session manager
            self.session[TRIBUNE_BAK_SESSION_NAME] = self.controller
            #self.session.modified = True
    
    def do_add(self):
        target = self.args.pop(0)
        pattern = ' '.join(self.args)
        self.controller.add_rule(target, pattern)
    
    def do_del(self):
        target = self.args.pop(0)
        pattern = ' '.join(self.args)
        self.controller.del_rule(target, pattern)
    
    def do_set(self):
        target = self.args.pop(0)
        kind = self.args.pop(0)
        pattern = ' '.join(self.args)
        self.controller.add_rule(target, pattern, kind)
    
    def do_remove(self):
        target = self.args.pop(0)
        kind = self.args.pop(0)
        pattern = ' '.join(self.args)
        self.controller.del_rule(target, pattern, kind)
    
    def do_load(self):
        self.controller.load()
    
    def do_save(self):
        self.controller.save()
    
    def do_on(self):
        self.controller.on()
    
    def do_off(self):
        self.controller.off()
    
    def do_reset(self):
        self.controller.off()

class CommandActionLastFM(CommandBase):
    """
    Use Lastfm to emit a 'musical instant' (eg: ``===> Moment The Beatles - Help <===``): ::

        /lastfm instant USERNAME
    
    Or for an registred user with the same username on lastfm and his tribune profile : ::

        /lastfm instant

    TODO: Add a new option 'name' to set a specific username (in session or cookies) 
          to use by default when no username is given in command;
    """
    required_args = 1
    need_to_push_data = True
    need_to_patch_response = True
    option_names = ('instant',)
    
    def __init__(self, *args, **kwargs):
        super(CommandActionLastFM, self).__init__(*args, **kwargs)
        self.track = None
        
    def validate(self):
        """
        Validation and pre-processing of request to LastFM
        """
        if not self.opt_name:
            raise ActionError(u"This action require at least one argument.")
        if self.opt_name not in self.option_names:
            raise ActionError(u"Unkown option '{0}' in your command action.".format(self.opt_name))
        
        # Do request with a valid username
        if len(self.args) > 0:
            self.track = self.get_current_track(self.args[0])
        elif self.author.is_authenticated():
            self.track = self.get_current_track(self.author.username)
        else:
            raise ActionError(u"No valid 'username' finded.".format(self.opt_name))
        
        return True
    
    def push_data(self, data):
        return self.push_current_track(self.track)
    
    def get_current_track(self, username):
        """
        Request LastFM API to get the current played track from an user
        
        This is raising exception ``ActionError`` for any error
        """
        params = urllib.urlencode({
            'user': username,
            'api_key': TRIBUNE_LASTFM_API_KEY,
            'method': 'user.getRecentTracks',
            'limit': 1, # Only need the last one
            'format': 'json',
        })
        client_headers = {'User-agent': 'djangotribune'}
        req = urllib2.Request(url=TRIBUNE_LASTFM_API_URL, data=params, headers=client_headers)
        
        try:
            fp = urllib2.urlopen(req)
        # Request Errors
        except urllib2.HTTPError, exception:
            raise ActionError("Error Http{0}".format(exception.code))
        except urllib2.URLError, exception:
            raise ActionError(exception.reason)
        # Succeeded Request
        else:
            data = json.loads(fp.read())
            
            # Error from LastFM API
            if 'error' in data:
                raise ActionError(data['message'])
            
            # Try to find a current played track
            last_track = data['recenttracks'].get('track', None)
            
            if not last_track:
                raise ActionError("No current track played")
            
            # API can return a list of dicts for the X+1 last recent tracks instead of a 
            # simple dict
            if isinstance(last_track, list):
                last_track = last_track[0]
            
            # If the track has a date field it is not a current played track, just the 
            # last recent track
            if 'date' in last_track:
                raise ActionError("No current track played")
                
            return last_track
        
        return None
    
    def push_current_track(self, last_track):
        """
        Push the combined track artist and track title in an *instant* as the new content 
        message to save
        """
        title = last_track['name']
        artist = last_track['artist']['#text']
        return {'content': u"<m>{artist} - {title}</m>".format(artist=artist, title=title)}

# A better, more pluggable system would be nice instead of this static register
TRIBUNE_COMMANDS = (
    #("admin", CommandAdmin),
    ("name", CommandActionName),
    ("nick", CommandActionName),
    ("bak", CommandBak),
    ("lastfm", CommandActionLastFM),
)
