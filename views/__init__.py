# -*- coding: utf-8 -*-
import datetime, json

from django import http
from django.views.generic.base import View

from djangotribune import TRIBUNE_LOCKED

def getmax_identity(accumulated, current, ua_cmp=lambda x:x, username_cmp=lambda x:x):
    """
    Find the higher identity width in all messages, to use with : ::
    
        ``reduce(getmax_identity, messages)``
    
    Optional arguments ``ua_cmp`` and ``username_cmp`` are function to apply transform 
    respectively on *user_agent* and *username* to calcul width
    """
    username = username_cmp(current['author__username'])
    if username and len(username)>accumulated:
        return len(current['author__username'])
    elif len(ua_cmp(current['user_agent']))>accumulated:
        return len(ua_cmp(current['user_agent']))
    return accumulated

class BackendEncoder(json.JSONEncoder):
    """Complex encoder for backend needs"""
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y%m%d%H%M%S')
        elif isinstance(obj, datetime.time):
            return obj.strftime("%H:%M:%S")
        return json.JSONEncoder.default(self, obj)

class LockView(View):
    """
    Base view for locked views
    
    TRIBUNE_LOCKED at True specify an authorized access only for authentified users.
    
    NOTE: Users Ban should be implemented here
    """
    def dispatch(self, request, *args, **kwargs):
        if TRIBUNE_LOCKED and request.user.is_anonymous():
            return http.HttpResponseForbidden()
        return super(LockView, self).dispatch(request, *args, **kwargs)
