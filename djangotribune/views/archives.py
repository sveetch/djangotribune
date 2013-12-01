# -*- coding: utf-8 -*-
import os, operator

from django import http
from django.db.models import Q
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.base import TemplateResponseMixin, View
from django.utils.http import urlquote

from djangotribune.models import Url
from djangotribune.forms import URLFILTERS_CHOICES, UrlSearchForm
from djangotribune.settings_local import TRIBUNE_ARCHIVE_URLS_MAX_LIMIT

class SearchListMixin(MultipleObjectMixin, FormMixin, TemplateResponseMixin):
    """
    Mixin to list and search on archived urls
    
    Form.save() have to be implemented in your form, it will return the 
    cleaned data to use to construct url arguments, initial datas and queryset 
    filters
    """
    url_search_start_arg = '&'
    
    def get_search_url_args(self):
        """
        Return the search's URL args to use in pagination URLs
        """
        if len(self.search_filters)>0:
            filter_args = ["{k}={v}".format(k=k,v=urlquote(v)) for k,v in self.search_filters]
            return self.url_search_start_arg+"&".join(filter_args)
        return ''

    def parse_search_url_args(self):
        """
        Get the given search filters from the URL arguments
        """
        filters = []
        for k,v in URLFILTERS_CHOICES:
            if self.request.GET.get(k):
                filters.append((k, self.request.GET.get(k)))
        return filters
    
    def get_queryset_filters(self):
        """
        Return args to add to queryset.filter()
        """
        if len(self.search_filters)>0:
            filters = [Q(**dict([item])) for item in self.search_filters]
            return reduce(operator.or_, filters)
        return None

    def get_queryset(self, form):
        """
        Return the queryset for url list, filtered from the search filters if given
        """
        q = super(SearchListMixin, self).get_queryset()
        filters = self.get_queryset_filters()
        if filters:
            q = q.filter(filters)
        return q
    
    def get_object_list(self, form):
        """
        Get the queryset for the list but knowing about the form to be able to 
        modify the queryset if needed
        """
        object_list = self.get_queryset(form)
        allow_empty = self.get_allow_empty()
        if not allow_empty and len(object_list) == 0:
            raise Http404(_(u"Empty list and '%(class_name)s.allow_empty' is False.")
                          % {'class_name': self.__class__.__name__})
        return object_list

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        context = super(SearchListMixin, self).get_context_data(**kwargs)
        context.update({
            'search_url_args': self.get_search_url_args()
        })

        return context

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        initial = super(SearchListMixin, self).get_initial()
        if len(self.search_filters)>0:
            filters = [k for k,v in self.search_filters]
            pattern = self.search_filters[0][1]
            initial.update({
                'pattern': pattern,
            })
        return initial

    def form_valid(self, form):
        self.object_list = self.get_object_list(form)
        return self.render_to_response(self.get_context_data(object_list=self.object_list, form=form))

    def form_invalid(self, form):
        self.object_list = self.get_object_list(form)
        return self.render_to_response(self.get_context_data(object_list=self.object_list, form=form))

class SearchListView(SearchListMixin, View):
    """
    View to list and search on archived urls
    """
    def get(self, *args, **kwargs):
        self.search_filters = self.parse_search_url_args()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        return self.form_valid(form)

    def post(self, request, *args, **kwargs):
        self.search_filters = self.parse_search_url_args()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            self.search_filters = form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class UrlArchivesView(SearchListView):
    """
    View to list and search on archived urls
    
    Form.save() have to be implemented in your form, it will return the 
    cleaned data to use to construct url arguments, initial datas and queryset 
    filters
    """
    model = Url
    allow_empty = True
    paginate_by = TRIBUNE_ARCHIVE_URLS_MAX_LIMIT
    template_name = "djangotribune/url_archives.html"
    initial = {'filters': [URLFILTERS_CHOICES[0][0]]}
    form_class = UrlSearchForm
    queryset = Url.objects.select_related('message', 'message__author').all().order_by('-created')
