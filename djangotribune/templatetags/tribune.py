# -*- coding: utf-8 -*-
from djangotribune.clocks import ClockIndice
from django import template

register = template.Library()

@register.filter(is_safe=True)
def indice_unicode(value):
    """
    Filter to format integer indices to their unicode version (like ``²``)
    
    It is needed because actually the ``ClockIndice`` instance is lost in the backend 
    that convert it to an integer version. This could be avoided.
    """
    return unicode(ClockIndice(value))