# -*- coding: utf-8 -*-
"""
Message backends views

RemoteBaseMixin is the base *Mixin for all remote mixins for various output format, 
it is where the format logic resides. But they are not views.

Further, the views are simple binding of RemoteBaseView plus their format mixins.

This is a simple system that allow to more flexible, besides the post views use the 
mixins to implement their formats.
"""
import json, texttable, pytz

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.db.models.query import QuerySet
from django.http import HttpResponseNotModified
from django.shortcuts import get_object_or_404
from django.views.decorators.http import condition
from django.utils.decorators import method_decorator
from django.utils import timezone

from djangotribune.settings_local import (TRIBUNE_MESSAGES_MAX_LIMIT, TRIBUNE_MESSAGES_DEFAULT_LIMIT, 
                                        TRIBUNE_BAK_SESSION_NAME)
from djangotribune.models import Channel, Message
from djangotribune.clocks import ClockIndice
from djangotribune.views import getmax_identity, BackendEncoder, ChannelAwareMixin, LockView

def last_modified_condition(request, *args, **kwargs):
    """
    Return the last modified date for message with queryset parameters (filters, 
    request arguments, etc..) for conditional view header purpose.
    
    Use directly the remote base mixin to correctly do the queryset.
    """
    remote = RemoteBaseMixin()
    remote.request = request
    remote.args = args
    remote.kwargs = kwargs
    last = remote.get_last_item()
    if last:
        return last.created
    return None

class RemoteBaseMixin(ChannelAwareMixin):
    """
    Remote base mixin implement all base stuff to generate a remote backend
    
    A view that inherit it must implement a correct ``build_backend`` methods.
    """
    http_method_names = ['get']
    clock_indexation = True
    http304_if_empty = True
    mimetype = "text/plain; charset=utf-8"
    default_row_direction = "desc"
    backend_type = "json" # can be (plain|json|xml|xml-crap)
    # ``clock`` and ``created`` fields are required if ``clock_indexation`` is actived
    remote_fields = ('clock', 'created', 'author__username', 'user_agent', 'raw')
    # Get the timezone to enforce, default to the defined one in settings, don't play with this
    current_tz = pytz.timezone(settings.TIME_ZONE)
    
    def force_datetime_tz(self, value):
        """
        Force timezone on datetime object
        """
        return value.astimezone(self.current_tz)

    def get_last_id(self):
        """
        Get the id from which to start fetching
        
        POST argument have predominance on GET argument that have predominance on 
        URL path element
        """
        last_id = self.kwargs.get('last_id', 0)
        last_id = self.request.GET.get('last_id', last_id)
        if self.request.POST:
            last_id = self.request.POST.get('last_id', last_id)
        try:
            last_id = int(last_id)
        except ValueError:
            return 0
            
        return last_id
    
    def get_row_direction(self):
        """Get row display direction from args if any"""
        direction = self.request.GET.get('direction', self.default_row_direction)
        if direction.lower() in ('asc', 'desc'):
            return direction
        return self.default_row_direction
    
    def get_backend_view_url(self):
        """Return the backend url, this is channel aware"""
        if hasattr(self, 'get_channel') and getattr(self, 'get_channel')():
            return reverse("tribune-channel-remote-{0}".format(self.backend_type), kwargs={'channel_slug':self.get_channel().slug})
        return reverse("tribune-remote-{0}".format(self.backend_type))
    
    def get_post_view_url(self):
        """Return the post url, this is channel aware"""
        if hasattr(self, 'get_channel') and getattr(self, 'get_channel')():
            return reverse("tribune-channel-post-{0}".format(self.backend_type), kwargs={'channel_slug':self.get_channel().slug})
        return reverse("tribune-post-{0}".format(self.backend_type))
    
    def get_clockfinder_view_url(self):
        """
        Return the clock finder url, this is channel aware
        
        We put the 00:00 clock pattern as a default, this is required to make a proper 
        reverse. This default pattern should be stripped by clients to use the 
        clockfinder url correctly.
        """
        if hasattr(self, 'get_channel') and getattr(self, 'get_channel')():
            return reverse("tribune-channel-clock-remote", kwargs={'clock': '00:00', 'channel_slug':self.get_channel().slug})
        return reverse("tribune-clock-remote", kwargs={'clock': '00:00'})
    
    def get_row_limit(self):
        """Get the row limit number to fetch"""
        try:
            limit = int(self.request.GET.get('limit', 0))
        except ValueError:
            limit = TRIBUNE_MESSAGES_DEFAULT_LIMIT
        finally:
            if not limit:
                limit = TRIBUNE_MESSAGES_DEFAULT_LIMIT
            elif limit > TRIBUNE_MESSAGES_MAX_LIMIT:
                limit = TRIBUNE_MESSAGES_MAX_LIMIT
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
    
    def get_last_item(self):
        """
        Return the last modified message using all queryset parameters applied
        
        This perform a query so this is not a method to call to know the last item from 
        a fetched backend.
        """
        limit = self.get_row_limit()
        last_id = self.get_last_id()
        direction = self.get_row_direction()
        channel = self.get_channel()
        bak = self.request.session.get(TRIBUNE_BAK_SESSION_NAME, None)
        filters = None
        if bak and bak.active:
            filters = bak.get_filters()
        try:
            last_item = Message.objects.get_backend(channel=channel, filters=filters, last_id=last_id).latest('created')
        except Message.DoesNotExist:
            return None
        else:
            return last_item
    
    def get_backend(self):
        """
        Return a messages list containing a dict for each message
        """
        self.user_owned_messages = self.get_user_owned_messages()
        
        limit = self.get_row_limit()
        last_id = self.get_last_id()
        direction = self.get_row_direction()
        channel = self.get_channel()
        # Build the queryset with filtering, base order, limit, etc..
        q = self.get_backend_queryset(channel, last_id, direction, limit)
        # Do we enforce the clock indexation or not ?
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

    def get_user_owned_messages(self):
        """
        Get saved user's message id saved in session
        """
        if self.request.user.is_authenticated():
            return []
        return self.request.session.get('tribune_owned_post_ids', [])
    
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
            this_date = self.force_datetime_tz(item['created']).strftime('%Y%m%d%H%M%S')

            if this_date in duplicates:
                duplicates[this_date] += 1
            else:
                duplicates[this_date] = 1
        # Apply the "real" indice to duplicates
        for item in backend:
            this_date = self.force_datetime_tz(item['created']).strftime('%Y%m%d%H%M%S')
            if this_date in duplicates:
                item['clock_indice'] = ClockIndice(duplicates[this_date])
                duplicates[this_date] = duplicates[this_date]-1
            else:
                item['clock_indice'] = ClockIndice(1)
            self.patch_row(item)
        return backend

    def patch_row(self, row):
        """
        For patching rows just after the backend has been fetched
        
        The problem :
        
        Because datetime objects are timezone aware and not time objects, it causes trouble in backend because created (datetime) is used to generate the id (time attribute in XML, created in others) then we use the clock (time) to display the clock. 
        
        So the datetime is resolved with a different timezone from the clock, and it results to have a different hour in id and clock. 
        
        This cause troubles for highlighted post, answer notification, and client parsing.
        
        The solution :
        
        * Force the configured timezone settings on used datetime from the database (else django try to resolve them from +0000)
        * Will be nice in Message entries to save the clock extracted from the datetime to ensure they allways be exactly the same (actually they differs only on microseconds)
        * The clock message stay to be used in specific queryset filters and instead we only use clock extraced from the localized datetime
        """
        # Allways forcing timezone
        row['created'] = self.force_datetime_tz(row['created'])
        # Replace the saved clock with the one from created to assure they allways are identical
        row['clock'] = row['created'].time()
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
        row = super(RemotePlainMixin, self).patch_row(row)
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

class RemoteTsvMixin(RemoteBaseMixin):
    """
    Remote TSV mixin
    """
    mimetype = "text/tab-separated-values; charset=utf-8"
    default_row_direction = "asc"
  
    def build_backend(self, messages):
        """
        A TSV backend:

        * served with HTTP Content-Type: text/tab-separated-values.
        * without header.
        * with a fixed list of fields

        Each line looks like:

        ${id}\t${time}\t${info}\t${login}\t${message}\n
        """
        
        backend = ''
        for item in messages:
            backend += str(item['id']) + "\t"
            backend += item['created'].strftime('%Y%m%d%H%M%S') + "\t"
            backend += item['user_agent'] + "\t"
            if item['author__username']:
                backend += item['author__username'];
            backend += "\t";
            backend += item['raw'] + "\n"
        
        return backend

class RemoteJsonMixin(RemoteBaseMixin):
    """
    Remote JSON mixin
    """
    mimetype = "application/json; charset=utf-8"
    remote_fields = ('id', 'created', 'clock', 'author__username', 'user_agent', 'web_render')
    default_row_direction = "asc"
    
    def build_backend(self, messages):
        if isinstance(messages, QuerySet):
            messages = list(messages)
        return json.dumps(messages, cls=BackendEncoder)

    def patch_row(self, row):
        """
        Add a *clockclass* suitable in ``class=""``, it's a combination of ``clock`` and 
        ``clock_indice`` (padded on two digits)
        """
        row = super(RemoteJsonMixin, self).patch_row(row)
        clock = row['clock'].strftime("%H%M%S")
        row['clockclass'] = clock + str(row.get('clock_indice', 1))
        row['clock_indice'] = row['clock_indice'].real
        # Add the owned mark if the message is authored by the current user
        row['owned'] = False
        if (self.request.user.is_authenticated() and row['author__username'] and self.request.user.username == row['author__username']) or (row['id'] in self.user_owned_messages):
            row['owned'] = True
        return row

class RemoteHtmlMixin(RemoteJsonMixin):
    """
    Remote Html mixin for template usage
    
    There is no real builded backend (as other backends) because it's the queryset that 
    is directly returned in the template. And some URL arguments are ignored because they 
    have no sense in this context.
    """
    def build_backend(self, messages):
        return messages

    def get_last_id(self):
        """Ignore 'last_id' option"""
        return 0
    
    def get_row_direction(self):
        """Ignore 'direction' option"""
        return self.default_row_direction

class RemoteXmlMixin(RemoteBaseMixin):
    """
    Remote XML mixin
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
            
            self.get_message_node(message_item, item['remote_render'])
        
        if self.prettify_backend:
            self._prettify(root)
        
        return ET.tostring(root, 'UTF-8')

    def get_message_node(self, parent_node, content):
        """
        Put content in <message/> node and give to eat to ET, this way all 
        content tags are not encoded
        """
        # Old behaviour with tag encoded
        #content = ET.SubElement(message_item, "message")
        #content.text = item['remote_render']
        node_str = u"<message>{content}</message>".format(content=content)
        parent_node.append(ET.fromstring(node_str.encode('utf-8')))
        
        return parent_node

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
    @method_decorator(condition(last_modified_func=last_modified_condition))
    def get(self, request, *args, **kwargs):
        messages = self.get_backend()
        if self.http304_if_empty and len(messages) == 0:
            return HttpResponseNotModified(mimetype=self.mimetype)
        
        backend = self.build_backend(messages)
        return self.patch_response( http.HttpResponse(backend, mimetype=self.mimetype) )

class RemotePlainView(RemotePlainMixin, RemoteBaseView):
    """
    Remote PLAIN TEXT view
    """
    pass

class RemoteTsvView(RemoteTsvMixin, RemoteBaseView):
    """
    Remote TSV view
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
