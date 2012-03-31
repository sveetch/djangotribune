# -*- coding: utf-8 -*-
"""
Root url's map for application
"""
from django.conf.urls.defaults import *

from djangotribune.views.help import ReadmePage
from djangotribune.views.remote import *

urlpatterns = patterns('',
    url(r'^readme/$', ReadmePage.as_view(), name='tribune-readme'),
    
    url(r'^remote/$', MessagePlainView.as_view(), name='tribune-remote-plain'),
    url(r'^remote/json/$', MessageJsonView.as_view(), name='tribune-remote-json'),
    url(r'^remote/xml/$', MessageXmlView.as_view(), name='tribune-remote-xml'),
    url(r'^remote/xml/crap/$', MessageCrapXmlView.as_view(), name='tribune-remote-xml-crap'),
)
