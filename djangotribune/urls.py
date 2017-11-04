# -*- coding: utf-8 -*-
"""
Root url's map for application
"""
from django.conf.urls.defaults import *

#from djangotribune.views.help import ReadmePage
from djangotribune.views.remote import (RemotePlainView, RemoteTsvView, RemoteJsonView, RemoteXmlView, 
                                        RemoteCrapXmlView)
from djangotribune.views.post import (PostBoardView, PostBoardNoScriptView, 
                                        PostRemotePlainView, PostRemoteTsvView, PostRemoteJsonView, 
                                        PostRemoteXmlView, PostRemoteCrapXmlView)
from djangotribune.views.clock import ClockJsonView
from djangotribune.views.discovery import ConfigDiscoveryView
from djangotribune.views.archives import UrlArchivesView

urlpatterns = patterns('',
    url(r'^$', PostBoardView.as_view(), name='tribune-board'),
    url(r'^noscript/$', PostBoardNoScriptView.as_view(), name='tribune-board-noscript'),
    
    #url(r'^readme/$', ReadmePage.as_view(), name='tribune-readme'),
    
    # For default tribune
    url(r'^discovery.config$', ConfigDiscoveryView.as_view(), name='tribune-config'),
    
    # Remote backend for specific targeted clocks
    url(r'^clock/(?P<clock>[:\d]{5,9})/$', ClockJsonView.as_view(), name='tribune-clock-remote'),
    
    # Message posting views
    url(r'^post/$', PostRemotePlainView.as_view(), name='tribune-post-plain'),
    url(r'^post/tsv/$', PostRemoteTsvView.as_view(), name='tribune-post-tsv'),
    url(r'^post/json/$', PostRemoteJsonView.as_view(), name='tribune-post-json'),
    url(r'^post/xml/$', PostRemoteXmlView.as_view(), name='tribune-post-xml'),
    url(r'^crap/post.xml$', PostRemoteCrapXmlView.as_view(), name='tribune-post-xml-crap'),
    
    # Remote backend views for message list
    url(r'^remote/$', RemotePlainView.as_view(), name='tribune-remote-plain'),
    url(r'^remote/tsv/$', RemoteTsvView.as_view(), name='tribune-remote-tsv'),
    url(r'^remote/json/$', RemoteJsonView.as_view(), name='tribune-remote-json'),
    url(r'^remote/xml/$', RemoteXmlView.as_view(), name='tribune-remote-xml'),
    url(r'^crap/remote.xml$', RemoteCrapXmlView.as_view(), name='tribune-remote-xml-crap'),
    
    # Message posting views
    url(r'^urls/$', UrlArchivesView.as_view(), name='tribune-url-archives'),
    
    # Duplicated previous urls for channel tribunes
    url(r'^(?P<channel_slug>[-\w]+)/$', PostBoardView.as_view(), name='tribune-channel-board'),
    url(r'^(?P<channel_slug>[-\w]+)/noscript/$', PostBoardNoScriptView.as_view(), name='tribune-channel-board-noscript'),
    
    url(r'^(?P<channel_slug>[-\w]+)/discovery.config', ConfigDiscoveryView.as_view(), name='tribune-channel-config'),
    #url(r'^(?P<channel_slug>[-\w]+)/crap/discovery.config', ConfigDiscoveryView.as_view(crap_mode=True), name='tribune-channel-config-crap'),
    
    url(r'^(?P<channel_slug>[-\w]+)/clock/(?P<clock>[:\d]{5,9})/$', ClockJsonView.as_view(), name='tribune-channel-clock-remote'),
    
    url(r'^(?P<channel_slug>[-\w]+)/post/$', PostRemotePlainView.as_view(), name='tribune-channel-post-plain'),
    url(r'^(?P<channel_slug>[-\w]+)/post/tsv/$', PostRemoteTsvView.as_view(), name='tribune-channel-post-tsv'),
    url(r'^(?P<channel_slug>[-\w]+)/post/json/$', PostRemoteJsonView.as_view(), name='tribune-channel-post-json'),
    url(r'^(?P<channel_slug>[-\w]+)/post/xml/$', PostRemoteXmlView.as_view(), name='tribune-channel-post-xml'),
    url(r'^(?P<channel_slug>[-\w]+)/crap/post.xml$', PostRemoteCrapXmlView.as_view(), name='tribune-channel-post-xml-crap'),
    
    url(r'^(?P<channel_slug>[-\w]+)/remote/$', RemotePlainView.as_view(), name='tribune-channel-remote-plain'),
    url(r'^(?P<channel_slug>[-\w]+)/remote/tsv/$', RemoteTsvView.as_view(), name='tribune-channel-remote-tsv'),
    url(r'^(?P<channel_slug>[-\w]+)/remote/json/$', RemoteJsonView.as_view(), name='tribune-channel-remote-json'),
    url(r'^(?P<channel_slug>[-\w]+)/remote/xml/$', RemoteXmlView.as_view(), name='tribune-channel-remote-xml'),
    url(r'^(?P<channel_slug>[-\w]+)/crap/remote.xml$', RemoteCrapXmlView.as_view(), name='tribune-channel-remote-xml-crap'),
)
