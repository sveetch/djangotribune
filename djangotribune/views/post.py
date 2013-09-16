# -*- coding: utf-8 -*-
"""
Message form views
"""
import random

from django import http
from django.views.generic.edit import BaseFormView, FormView
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator

from djangotribune.settings_local import TRIBUNE_TITLES
from djangotribune.models import Channel, Message
from djangotribune.forms import MessageForm
from djangotribune.views import LockView
from djangotribune.views.remote import RemoteBaseMixin, RemotePlainMixin, RemoteHtmlMixin, RemoteJsonMixin, RemoteXmlMixin
from djangotribune.actions import CommandBase

class PostBaseView(LockView, FormView):
    """Base POST view"""
    form_class = MessageForm
    
    def get_form_kwargs(self):
        kwargs = super(PostBaseView, self).get_form_kwargs()
        kwargs.update({
            'headers': self.request.META,
            'cookies': self.request.COOKIES,
            'session': self.request.session,
            'author': self.request.user,
            'channel': self.get_channel(),
        })
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        self.command = form.command
        return super(PostBaseView, self).form_valid(form)

class PostRemoteBaseView(RemoteBaseMixin, PostBaseView):
    """
    Remote POST base view
    
    Exempted of CSRF usage and directly return the backend after receiving the message
    
    This view need to be inherited with a Remote mixin because it use the 
    ``build_backend`` method
    
    Remote post views raise an http error 400 (Bad Request) in case of form error with an 
    explanation.
    """
    http_method_names = ['post', 'put']
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(PostRemoteBaseView, self).dispatch(*args, **kwargs)
        
    def get_success_url(self):
        """
        Dummy method to satisfy the ``FormView.form_valid`` method
        
        The returned URL is never used
        """
        return ''
    
    def form_valid(self, form):
        super(PostRemoteBaseView, self).form_valid(form)
        
        messages = self.get_backend()
        backend = self.build_backend(messages)
        
        return self.patch_response( http.HttpResponse(backend, mimetype=self.mimetype) )

    def form_invalid(self, form):
        errors = []
        for k,v in form.errors.items():
            errors.append(u"{fieldname}: {errs}".format(fieldname=k, errs=u" ".join(v)))
        errors_display = u"* {0}".format("\n* ".join(errors))
        # Errors is always returned with the plain/text mimetype
        return http.HttpResponseBadRequest(errors_display, mimetype=RemotePlainMixin.mimetype)
    
    def patch_response(self, response):
        response = super(PostRemoteBaseView, self).patch_response(response)
        
        # When form results in a new message, push his id to a private response header
        if hasattr(self, 'object') and self.object:
            response['X-Post-Id'] = self.object.id
        
        # When form has a command that needs to patch response
        if self.command and self.command.need_to_patch_response:
            self.command.patch_response(response)
        
        return response

class PostBoardView(RemoteHtmlMixin, PostBaseView):
    """
    HTML Interface view
    
    This view combine the Remote methods (to display messages in template) and Post 
    methods
    """
    http_method_names = ['get', 'post', 'put', 'delete', 'head', 'options', 'trace']
    template_name = "djangotribune/board.html"
    clock_indexation = True
    
    def get_context_data(self, **kwargs):
        # Bubble up some data to the board context
        kwargs = super(PostBoardView, self).get_context_data(**kwargs)
        kwargs.update({
            'board_title': self.get_board_title(),
            'message_list': self.get_backend(),
            'message_display_limit': self.get_row_limit(), # used by rich interface as the display limit
            'tribune_channel': self.get_channel(),
            'tribune_backend_url': self.get_backend_view_url(),
            'tribune_post_url': self.get_post_view_url(),
            'clockfinder_url': self.get_clockfinder_view_url(),
        })
        return kwargs
    
    def get_board_title(self):
        """
        Get a random title from ``TRIBUNE_TITLES``
        
        Only used by some special backends
        """
        return TRIBUNE_TITLES[ random.randrange(0, len(TRIBUNE_TITLES)) ]
    
    def form_valid(self, form):
        response = super(PostBoardView, self).form_valid(form)
        return self.patch_response( response )
    
    def patch_response(self, response):
        response = super(PostBoardView, self).patch_response(response)
        
        # When form result in a new message, push his id in response headers
        if hasattr(self, 'object') and self.object:
            response['X-Post-Id'] = self.object.id
        
        # When form has a command that needs to patch response
        if self.command and self.command.need_to_patch_response:
            self.command.patch_response(response)
        
        return response
        
    def get_success_url(self):
        """
        Return the 'redirect to' URL (with URL arguments if any) after a validated 
        form request
        """
        return self.get_redirect_url(reverse('tribune-board'))

class PostBoardNoScriptView(PostBoardView):
    """
    HTML Interface view duplicata with different template
    """
    template_name = "djangotribune/board_noscript.html"

class PostRemotePlainView(RemotePlainMixin, PostRemoteBaseView):
    """
    Remote PLAIN TEXT view
    """
    pass

class PostRemoteJsonView(RemoteJsonMixin, PostRemoteBaseView):
    """
    Remote JSON view
    """
    pass

class PostRemoteXmlView(RemoteXmlMixin, PostRemoteBaseView):
    """
    Remote JSON view
    """
    pass

class PostRemoteCrapXmlView(RemoteXmlMixin, PostRemoteBaseView):
    """
    Remote XML view with indent (for some very old client application)
    """
    prettify_backend = True
