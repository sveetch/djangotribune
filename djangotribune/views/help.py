# -*- coding: utf-8 -*-
"""
View to display help 

DEPRECATED: now we use the doc on readthedoc
"""
import os

from django import http
from django.views.generic.base import TemplateView

import djangotribune

class DummySourceParser(object):
    """Dummy parser, return the source untransformed"""
    def __init__(self, source, *args, **kwargs):
        self.source = source
    def __str__(self):
        return self.source
    def __unicode__(self):
        return self.source.decode('utf-8')
    def __repr__(self):
        return "<DummySourceParser>"

try:
    from rstview.parser import SourceParser
except ImportError:
    class SourceParser(DummySourceParser): pass

class ConditionalParserView(TemplateView):
    """
    Page with conditional render and mimetype
    
    Si le parser de rstview est disponible, renvoi une réponse HTML avec 
    le contenu transformé par docutils.
    
    Sinon renvoi une réponse plain-text avec directement le contenu du document 
    sans transformation.
    
    L'encoding attendu du document source est *utf-8*.
    """
    template_name = "djangotribune/help.html"
    source_doc_name = "README.rst"
    source_doc_title = "README"
    
    def get(self, request, *args, **kwargs):
        tribune_root = os.path.abspath(os.path.dirname(djangotribune.__file__))
        f = open(os.path.join(tribune_root, self.source_doc_name))
        content = SourceParser(f.read(), initial_header_level=1, silent=False)
        f.close()
        
        if isinstance(content, DummySourceParser):
            return self.plain_response(content)
        return self.html_response(content)
    
    def plain_response(self, content):
        return http.HttpResponse(content, mimetype="text/plain; charset=utf-8")
    
    def html_response(self, content):
        context = {'content' : content, 'doc_title' : self.source_doc_title}
        return self.render_to_response(context)

class ReadmePage(ConditionalParserView):
    """
    Page d'aide sur le module
    """
    source_doc_name = "../README.rst"
    source_doc_title = "Sveetchies-tribune"
