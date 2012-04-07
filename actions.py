# -*- coding: utf-8 -*-
"""
Message commands parser

Action idea to implement (or not)
=================================

Flood tribune with some pre-registred message(s) (must be reserved to admins at less): ::

    /flood FLOODNAME

Use Lastfm to emit a 'musical instant' (eg: ``===> Moment The Beatles - Help <===``): ::

    /lastfm instant USERNAME

BAK actions
-----------

This register message filters ``djangotribune.models.FilterEntry`` to filter message on 
some pattern.

To enable filters usage : ::

    /bak on

To disable filters usage : ::

    /bak off

To add a new filter : ::

    /bak add TARGET KIND PATTERN

To delete a registred filter : ::

    /bak del TARGET KIND PATTERN


"""
import datetime
from base64 import b64encode

from django.conf import settings

from djangotribune import TRIBUNE_MESSAGES_UA_COOKIE_NAME, TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, TRIBUNE_MESSAGES_UA_LENGTH_MIN

class CommandBase(object):
    """Base command action"""
    required_args = 0
    
    def __init__(self, args):
        self.args = args
    
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
    def __init__(self, args):
        super(CommandActionName, self).__init__(args)
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
        """
        # Set the cookie to save the new name
        if self.new_name and len(self.new_name) >= TRIBUNE_MESSAGES_UA_LENGTH_MIN:
            response.set_cookie(TRIBUNE_MESSAGES_UA_COOKIE_NAME, b64encode(self.new_name), max_age=TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, expires=self.expires, domain=settings.SESSION_COOKIE_DOMAIN)
        # Delete the cookie to drop custom name
        else:
            response.set_cookie(TRIBUNE_MESSAGES_UA_COOKIE_NAME, '', max_age=TRIBUNE_MESSAGES_UA_COOKIE_MAXAGE, expires=self.expires, domain=settings.SESSION_COOKIE_DOMAIN) # Is this really necessary ?
            response.delete_cookie(TRIBUNE_MESSAGES_UA_COOKIE_NAME)
        
        return response

TRIBUNE_COMMANDS = (
    #("admin", CommandAdmin),
    ("name", CommandActionName),
    #("bak", CommandBak),
)
