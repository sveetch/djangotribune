# -*- coding: utf-8 -*-
"""
Message backends views
"""
import json, texttable

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from django import http
from django.db.models.query import QuerySet
from django.contrib.sites.models import Site
from django.shortcuts import get_object_or_404

from djangotribune import TRIBUNE_MESSAGES_MAX_LIMIT, TRIBUNE_MESSAGES_DEFAULT_LIMIT, TRIBUNE_BAK_SESSION_NAME
from djangotribune.models import Channel, Message
from djangotribune.clocks import ClockIndice
from djangotribune.views import getmax_identity, BackendEncoder, LockView

class RemoteBaseMixin(object):
    """
    This Mixin implement all base stuff to generate a remote backend
    
    But a view must implement his correct ``build_backend`` methods.
    """
    http_method_names = ['get']
    clock_indexation = True
    mimetype = "text/plain; charset=utf-8"
    default_row_direction = "desc"
    # ``clock`` and ``created`` fields are required if ``clock_indexation`` is actived
    remote_fields = ('clock', 'created', 'author__username', 'user_agent', 'raw')

    def get_channel(self):
        """Get the channel to fetch messages"""
        memokey = '_cache_get_channel'
        if not hasattr(self, memokey):
            if self.request.GET.get('channel', None):
                channel = get_object_or_404(Channel, slug=self.request.GET['channel'])
            else:
                channel = None
            setattr(self, memokey, channel)
        return getattr(self, memokey)

    def get_last_id(self):
        """Get the id from wich to start row fetching"""
        last_id = self.kwargs.get('last_id', 0)
        last_id = self.request.GET.get('last_id', last_id)
        return last_id
    
    def get_row_direction(self):
        """Get row display direction from args if any"""
        direction = self.request.GET.get('direction', self.default_row_direction)
        if direction.lower() in ('asc', 'desc'):
            return direction
        return self.default_row_direction
    
    def get_row_limit(self):
        """Get the row limit number to fetch"""
        try:
            limit = int(self.request.GET.get('limit', 0))
        except ValueError:
            limit = TRIBUNE_MESSAGES_DEFAULT_LIMIT
        finally:
            if limit == 0 or limit > TRIBUNE_MESSAGES_MAX_LIMIT:
                limit = TRIBUNE_MESSAGES_DEFAULT_LIMIT
        return limit
    
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
        return Message.objects.get_backend(channel=channel, filters=filters, last_id=last_id).values(*self.remote_fields)[:limit]
    
    def get_backend(self):
        """
        Return a messages list containing a dict for each message
        """
        limit = self.get_row_limit()
        last_id = self.get_last_id()
        direction = self.get_row_direction()
        channel = self.get_channel()
        # Build the queryset with filtering, base order, limit, etc..
        q = self.get_backend_queryset(channel, last_id, direction, limit)
        # Clock indexation
        if self.clock_indexation:
            q = self.clock_indexing(q)
        else:
            q = map(self.patch_row, q)
        # Change direction if option is "asc", default is desc
        if direction == 'asc':
            if isinstance(q, QuerySet):
                q = list(q)
            q.reverse()
        return q

    def get_redirect_url(self, url):
        """Return the URL 'redirect to' with the URL args if any"""
        args = self.request.META["QUERY_STRING"]
        if args:
            url = "{0}?{1}".format(url, args)
        return url

    def build_backend(self, messages):
        return 'Hello World'
    
    def clock_indexing(self, backend):
        """
        Same clock indexation
        
        Linear identical clocks are marked with an indice called "clock indice" (or 
        *brother indice*), a brother clock recover the previous indice incremented.
        
        This method use actually a double pass through on the message list.
        """
        # Count all duplicate clock and store them in a registry
        duplicates = {}
        for item in backend:
            this_date = item['created'].strftime('%Y%m%d%H%M%S')
            if this_date in duplicates:
                duplicates[this_date] += 1
            else:
                duplicates[this_date] = 1
        # Apply the "real" indice to duplicates
        for item in backend:
            this_date = item['created'].strftime('%Y%m%d%H%M%S')
            this_clock = item['clock'].strftime('%H:%M:%S')
            if this_date in duplicates:
                item['clock_indice'] = ClockIndice(duplicates[this_date])
                duplicates[this_date] = duplicates[this_date]-1
            else:
                item['clock_indice'] = ClockIndice(1)
            self.patch_row(item)
        return backend

    def patch_row(self, row):
        """
        For patching rows
        
        Do nothing by default
        """
        return row
    
    def patch_response(self, response):
        """
        For patching response like headers injection, etc..
        
        By default this add cache information to avoid remotes caching by browsers
        """
        response['Pragma'] = "no-cache"
        response['Cache-Control'] = "no-cache, no-store, must-revalidate, max-age=0" 
        return response

class RemotePlainMixin(RemoteBaseMixin):
    """
    Remote PLAIN TEXT mixin
    """
    default_row_direction = "asc"

    def patch_row(self, row):
        row['user_agent'] = row['user_agent'][:30]
        return row
    
    def build_backend(self, messages):
        """
        Plain/text backend is just a row list of messages with three columns (clock, 
        identity, message) tabulated and optionnaly an header title
        
        * Clock column width is always fixed on 10 characters;
        * Identity column width is aligned on the biggest identity (username or 
          user_agent);
        * Message column takes the size left in the table maximum width.
        """
        clock_col_width = 10
        default_table_width = 90
        max_table_width = 600
        
        try:
            table_width = int(self.request.GET.get('table_width', default_table_width))
        except ValueError:
            table_width = default_table_width
        else:
            if table_width > max_table_width:
                table_width = max_table_width
        
        username_modifier = lambda x: u"<{0}>".format(x)
        identity_col_width = reduce(lambda x,y: getmax_identity(x,y, username_cmp=username_modifier), messages, 10)
        
        table = texttable.Texttable()
        table.set_deco(texttable.Texttable.HEADER)
        table.set_cols_dtype(["t", "t", "t"])
        table.set_cols_align(["l", "l", "l"])
        table.set_cols_valign(["t", "t", "t"])
        table.set_cols_width([clock_col_width, identity_col_width, table_width-identity_col_width-clock_col_width])
        
        for item in messages:
            clock = item['clock'].strftime("%H:%M:%S")
            if int(item.get('clock_indice', 1)) > 1:
                clock += unicode(item['clock_indice'])
            
            identity = item['user_agent']
            if item['author__username']:
                identity = username_modifier(item['author__username'])
            
            message = item['raw']
            
            table.add_row( (clock.encode('utf-8'), identity.encode('utf-8'), message.encode('utf-8')) )
        
        return table.draw()

class RemoteJsonMixin(RemoteBaseMixin):
    """
    Remote JSON
    """
    mimetype = "application/json; charset=utf-8"
    remote_fields = ('id', 'created', 'clock', 'author__username', 'user_agent', 'web_render')
    
    def build_backend(self, messages):
        if isinstance(messages, QuerySet):
            messages = list(messages)
        return json.dumps(messages, cls=BackendEncoder)

    def patch_row(self, row):
        """
        Add a *clockclass* suitable in ``class=""``, it's a combination of ``clock`` and 
        ``clock_indice`` (padded on two digits)
        """
        row['clockclass'] = row['clock'].strftime("%H%M%S") + str(row.get('clock_indice', 1))
        return row

class RemoteHtmlMixin(RemoteJsonMixin):
    """
    Remote Html for template usage
    
    There is no real builded backend as this is the queryset that is returned in the 
    template. And some URL argument are ignored thus they have no sense in this context.
    """
    default_row_direction = "asc"
    def build_backend(self, messages):
        return messages

    def patch_row(self, row):
        row['user_agent'] = row['user_agent'][:30]
        return row

    def get_last_id(self):
        """Ignore 'last_id' option"""
        return 0
    
    def get_row_direction(self):
        """Ignore 'direction' option"""
        return self.default_row_direction

class RemoteXmlMixin(RemoteBaseMixin):
    """
    Remote XML
    """
    clock_indexation = False
    prettify_backend = False
    mimetype = "application/xml; charset=utf-8"
    remote_fields = ('id', 'created', 'author__username', 'user_agent', 'remote_render')
    
    def build_backend(self, messages):
        root = ET.Element("board")
        root.set('site', "http://{0}".format(Site.objects.get_current().domain))

        for item in messages:
            message_item = ET.SubElement(root, "post")
            message_item.set('id', str(item['id']))
            message_item.set('time', item['created'].strftime('%Y%m%d%H%M%S'))

            user_agent = ET.SubElement(message_item, "info")
            user_agent.text = item['user_agent']
            
            username = ET.SubElement(message_item, "login")
            if item['author__username']:
                username.text = item['author__username']
            
            content = ET.SubElement(message_item, "message")
            content.text = item['remote_render']

        if self.prettify_backend:
            self._prettify(root)
        
        return ET.tostring(root, 'UTF-8')

    def _prettify(self, elem, level=0):
        """Prettify an ElementTree with indent"""
        i = "\n" + level*" "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + " "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._prettify(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

class RemoteBaseView(LockView):
    """
    Remote base view is not intended to be used as a real view, this is just the base 
    implementation view to be inherited with a remote mixin
    """
    def get(self, request, *args, **kwargs):
        messages = self.get_backend()
        backend = self.build_backend(messages)
        return self.patch_response( http.HttpResponse(backend, mimetype=self.mimetype) )

class RemotePlainView(RemotePlainMixin, RemoteBaseView):
    """
    Remote PLAIN TEXT view
    """
    pass

class RemoteJsonView(RemoteJsonMixin, RemoteBaseView):
    """
    Remote JSON view
    """
    pass

class RemoteXmlView(RemoteXmlMixin, RemoteBaseView):
    """
    Remote XML view
    """
    pass

class RemoteCrapXmlView(RemoteXmlView):
    """
    Remote XML view with indent (for some very old client application)
    """
    prettify_backend = True
