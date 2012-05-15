# -*- coding: utf-8 -*-
"""
Root url's map for application
"""
from django.conf.urls.defaults import *

from djangotribune.views.help import ReadmePage
from djangotribune.views.remote import (RemotePlainView, RemoteJsonView, RemoteXmlView, 
                                        RemoteCrapXmlView)
from djangotribune.views.post import (PostBoardView, PostBoardNoScriptView, 
                                        PostRemotePlainView, PostRemoteJsonView, 
                                        PostRemoteXmlView, PostRemoteCrapXmlView)

urlpatterns = patterns('',
    url(r'^$', PostBoardView.as_view(), name='tribune-board'),
    url(r'^noscript/$', PostBoardNoScriptView.as_view(), name='tribune-board-noscript'),
    
    url(r'^readme/$', ReadmePage.as_view(), name='tribune-readme'),
    
    url(r'^post/$', PostRemotePlainView.as_view(), name='tribune-post-plain'),
    url(r'^post/json/$', PostRemoteJsonView.as_view(), name='tribune-post-json'),
    url(r'^post/xml/$', PostRemoteXmlView.as_view(), name='tribune-post-xml'),
    url(r'^post/xml/crap/$', PostRemoteCrapXmlView.as_view(), name='tribune-post-xml-crap'),
    
    url(r'^remote/$', RemotePlainView.as_view(), name='tribune-remote-plain'),
    url(r'^remote/json/$', RemoteJsonView.as_view(), name='tribune-remote-json'),
    url(r'^remote/xml/$', RemoteXmlView.as_view(), name='tribune-remote-xml'),
    url(r'^remote/xml/crap/$', RemoteCrapXmlView.as_view(), name='tribune-remote-xml-crap'),
)
