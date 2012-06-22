# -*- coding: utf-8 -*-
"""
Message backends views

RemoteBaseMixin is the base *Mixin for all remote mixins for various output format, 
it is where the format logic resides. But they are not views.

Further, the views are simple binding of RemoteBaseView plus their format mixins.

This is a simple system that allow to more flexible, besides the post views use the 
mixins to implement their formats.
"""
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from django import http
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse

from djangotribune.settings_local import TRIBUNE_LOCKED, TRIBUNE_MESSAGES_POST_MAX_LENGTH, TRIBUNE_INTERFACE_REFRESH_SHIFTING
from djangotribune.models import Channel
from djangotribune.views import ChannelAwareMixin, LockView
from djangotribune import __version__ as djangotribune_version

class ConfigDiscoveryView(ChannelAwareMixin, LockView):
    """
    XML view to display tribune config for third application clients
    """
    mimetype = "application/xml; charset=utf-8"
    
    def build_backend(self):
        current_site = Site.objects.get_current()
        channel = self.get_channel()
        # Some variables to adjust according to the channel
        site_title = current_site.name
        board_title = "Tribune"
        backend_url = reverse("tribune-remote-xml")
        post_url = reverse("tribune-post-xml")
        if channel:
            site_title = u"{site_title} - {channel}".format(site_title=site_title, channel=channel.title)
            board_title = u"Tribune /{0}/".format(channel.slug)
            backend_url = reverse("tribune-channel-remote-xml", kwargs={'channel_slug':channel.slug})
            post_url = reverse("tribune-channel-post-xml", kwargs={'channel_slug':channel.slug})
        
        root = ET.Element("site")
        root.set('baseurl', "http://{0}".format(current_site.domain))
        root.set('title', site_title)
        root.set('name', site_title)
        root.set('version', djangotribune_version)

        board_element = ET.SubElement(root, "board")
        board_element.set('name', "board")
        board_element.set('title', board_title)

        backend_element = ET.SubElement(board_element, "backend")
        backend_element.set('path', backend_url)
        backend_element.set('tags_encoded', "true")
        backend_element.set('refresh', str((TRIBUNE_INTERFACE_REFRESH_SHIFTING/1000))) # conversion des ms en secondes
        backend_element.set('public', str(not(TRIBUNE_LOCKED)).lower())

        post_element = ET.SubElement(board_element, "post")
        post_element.set('path', post_url)
        post_element.set('method', "post")
        post_element.set('anonymous', str(not(TRIBUNE_LOCKED)).lower())
        post_element.set('max_length', str(TRIBUNE_MESSAGES_POST_MAX_LENGTH))

        field_element = ET.SubElement(post_element, "field")
        field_element.set('name', "content")
        field_element.text = "$m"
        
        return ET.tostring(root, 'UTF-8')
    
    def get(self, request, *args, **kwargs):
        backend = self.build_backend()
        return http.HttpResponse(backend, mimetype=self.mimetype)

