# -*- coding: utf-8 -*-
"""
Clock backends views
"""

from django import http
from django.views.generic.edit import BaseFormView, FormView
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator

from djangotribune.models import Channel, Message
from djangotribune.settings_local import TRIBUNE_BAK_SESSION_NAME
from djangotribune.views.remote import RemoteBaseView, RemoteJsonMixin
from djangotribune.clocks import ClockstampManipulator

class ClockJsonView(RemoteJsonMixin, RemoteBaseView):
    """
    Remote JSON view for targeted clock
    
    In fact this more than a clock, this can be a flat clock or even a full timestamp
    """
    def get_backend_queryset(self, channel, last_id, direction, limit):
        """
        Get the queryset to fetch messages with options from args/kwargs
        
        If the user session contain a BaK controller, it will be used to extract filters 
        and apply them.
        
        The returned queryset contains only dicts of messages (where each dict is a 
        message), mapped key comes from ``self.remote_fields``.
        """
        bak = self.request.session.get(TRIBUNE_BAK_SESSION_NAME, None)
        filters = None
        if bak and bak.active:
            filters = bak.get_filters()
        
        # Lecture et reconnaissance du timestamp
        self.clock = ClockstampManipulator(clockstamp=self.kwargs['clock'])
        print "is_valid:", self.clock.is_valid
        print "is_datetime:", self.clock.is_datetime
        print "get_clock_object:", self.clock.get_clock_object()
        
        q = Message.objects
        if self.clock.is_valid:
            q = q.filter(**self.clock.get_lookup())
        
        # TODO: raise error if clock is invalid ?
        return q.get_backend(channel=channel, filters=filters, last_id=last_id).values(*self.remote_fields)[:limit]
