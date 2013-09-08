# -*- coding: utf-8 -*-
"""
Clock backends views
"""
from django import http
from djangotribune.models import Message
from djangotribune.settings_local import TRIBUNE_BAK_SESSION_NAME
from djangotribune.views.remote import RemoteBaseView, RemotePlainMixin, RemoteJsonMixin
from djangotribune.clocks import PARSER_EXCEPTION_TYPERROR_EXPLAIN, ClockParser

class ClockJsonView(RemoteJsonMixin, RemoteBaseView):
    """
    Remote JSON view for targeted clock
    """
    http304_if_empty = False
    
    def get(self, request, *args, **kwargs):
        """
        Overwrite get method to perform clock format validation then raise a 
        Http400 if not valid
        """
        _p = ClockParser()
        if not _p.is_valid(self.kwargs['clock']):
            return http.HttpResponseBadRequest(PARSER_EXCEPTION_TYPERROR_EXPLAIN, mimetype=RemotePlainMixin.mimetype)
        return super(ClockJsonView, self).get(request, *args, **kwargs)

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
        _p = ClockParser()
        
        q = Message.objects
        q = q.filter(**_p.get_time_lookup(self.kwargs['clock']))
        
        # TODO: raise error if clock is invalid
        return q.get_backend(channel=channel, filters=filters, last_id=last_id).values(*self.remote_fields)[:limit]
