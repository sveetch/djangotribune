# -*- coding: utf-8 -*-
"""
Application Crumbs
"""
from autobreadcrumbs import site
from django.utils.translation import ugettext_lazy

site.update({
    'tribune-board': ugettext_lazy('Tribune'),
    'tribune-channel-board': "{{ tribune_channel.title }}",
    'tribune-board-noscript': ugettext_lazy('No script'),
    'tribune-readme': ugettext_lazy('Readme'),
    'tribune-url-archives': ugettext_lazy('Url archives'),
})
