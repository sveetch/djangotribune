# -*- coding: utf-8 -*-
"""
Message commands parser

Action idea to implement (or not)
=================================

Flood tribune with some pre-registred message(s) (must be reserved to admins at less): ::

    /flood FLOODNAME

Use Lastfm to emit a 'musical instant' (eg: ``===> Moment The Beatles - Help <===``): ::

    /lastfm instant USERNAME

"""
import datetime
from base64 import b64encode

from django.conf import settings

from djangotribune import TRIBUNE_MESSAGES_UA_COOKIE_NAME, TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, TRIBUNE_MESSAGES_UA_LENGTH_MIN, TRIBUNE_BAK_SESSION_NAME
from djangotribune.models import FILTER_TARGET_CHOICE, FILTER_TARGET_ALIASES, FILTER_KIND_ALIASES
from djangotribune.bak import BakController

class CommandBase(object):
    """Base command action"""
    required_args = 0
    
    def __init__(self, args, author, cookies, session):
        self.args = args
        self.author = author
        self.cookies = cookies
        self.session = session
    
    def validate(self):
        return True
    
    def execute(self):
        self.do_dummy()
    
    def patch_response(self, response):
        return response
    
    def do_dummy(self):
        print "Dummy action is dummy"

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
        
    def patch_response(self, response):
        """
        Patch response to set or update cookie
        
        TODO: Can't we just use ``self.cookies`` instead of patching response for 
              set/delete cookie ?
        """
        # Set the cookie to save the new name
        if self.new_name and len(self.new_name) >= TRIBUNE_MESSAGES_UA_LENGTH_MIN:
            response.set_cookie(TRIBUNE_MESSAGES_UA_COOKIE_NAME, b64encode(self.new_name), max_age=TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, expires=self.expires, domain=settings.SESSION_COOKIE_DOMAIN)
        # Delete the cookie to drop custom name
        else:
            response.set_cookie(TRIBUNE_MESSAGES_UA_COOKIE_NAME, '', max_age=TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, expires=self.expires, domain=settings.SESSION_COOKIE_DOMAIN) # Is this really necessary ?
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
    option_names = ('on', 'off', 'add', 'set', 'del', 'remove', 'save', 'load', 'reset')
    short_options = ('on', 'off', 'save', 'load', 'reset') # options than didn't need arguments
    lv1_options = ('add', 'del') # options than require only one argument
    lv2_options = ('set', 'remove') # options than require only two argument
    
    def __init__(self, *args, **kwargs):
        super(CommandBak, self).__init__(*args, **kwargs)
        self.opt_name = self.args.pop(0)
        self.controller = None
        
        self.available_filter_targets = dict(FILTER_TARGET_ALIASES).keys()
        self.available_filter_kinds = dict(FILTER_KIND_ALIASES).keys()
        
    def validate(self):
        # Is an allowed option name
        if self.opt_name not in self.option_names:
            return False
        # Some options requires arguments
        # This is tricky but there are few option and not many different option needs
        if self.opt_name not in self.short_options:
            if self.opt_name in self.lv1_options:
                if len(self.args)<2:
                    return False
                elif self.args[0] not in self.available_filter_targets:
                    return False
            elif self.opt_name in self.lv2_options:
                if len(self.args)<3:
                    return False
                elif self.args[0] not in self.available_filter_targets:
                    return False
                elif self.args[1] not in self.available_filter_kinds:
                    return False
            
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

# A better, more pluggable system would be nice instead of this static register
TRIBUNE_COMMANDS = (
    #("admin", CommandAdmin),
    ("name", CommandActionName),
    ("bak", CommandBak),
)
