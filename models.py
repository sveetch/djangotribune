# -*- coding: utf-8 -*-
"""
Data Models
"""
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext as _

from django.contrib.auth.models import User

# Target determines wich field is used on the filter
FILTER_TARGET_CHOICE = (
    ('user_agent', 'User Agent'),
    ('author__username', 'Username'),
    ('raw', 'Raw message'),
)
# Kind determines what kind of Field lookup is used on the filter
# TODO: Add 'startswith' and 'endswith' kinds and remember to limit or disable the 
#      'regex' kinds (that seems to have too much cost on performance)
FILTER_KIND_CHOICE = (
    ('regex', 'Case-sensitive regular expression match'),
    ('iregex', 'Case-insensitive regular expression match'),
    ('contains', 'Case-sensitive containment test'),
    ('icontains', 'Case-insensitive containment test'),
    ('exact', 'Case-sensitive exact match'),
    ('iexact', 'Case-insensitive exact match'),
)

class Channel(models.Model):
    """
    Channel
    """
    created = models.DateTimeField(_('created date'), auto_now_add=True)
    slug = models.SlugField('slug', unique=True, max_length=75)
    title = models.CharField(_('title'), max_length=55, blank=False)
    
    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('channel')
        verbose_name_plural = _('channels')

class UserPreferences(models.Model):
    """
    User preferences to tribune usage
    """
    owner = models.ForeignKey(User, verbose_name=_('owner'), unique=True, blank=False)
    created = models.DateTimeField(_('created date'), auto_now_add=True)
    refresh_time = models.IntegerField(_('refresh time'), blank=False, default=5000)
    refresh_actived = models.BooleanField(_('refresh actived'), default=True)
    smileys_host_url = models.CharField(_('smileys host url'), max_length=150, blank=False)
    maximised = models.BooleanField(_('maximised view'), default=True)
    
    def __unicode__(self):
        return self.owner.username

    class Meta:
        verbose_name = _('user preference')
        verbose_name_plural = _('user preferences')

class FilterEntryManager(models.Manager):
    """
    FilterEntry manager
    """
    def get_filters_args(self):
        """Return filters as a tuple of dict kwargs"""
        args = []
        for item in self.get_query_set().all():
            key = "{target}__{kindfunc}".format(target=item.target, kindfunc=item.kind)
            args.append( {key: item.value} )
        return tuple(args)

class FilterEntry(models.Model):
    """
    Personnal user entry to hide messages
    
    NOTE: Users should have a limit to use filter to avoid too much ressources usage on 
          database ?
    """
    author = models.ForeignKey(User, verbose_name=_('identified author'), blank=False)
    target = models.CharField(_('target'), choices=FILTER_TARGET_CHOICE, max_length=30, blank=False)
    kind = models.CharField(_('kind'), choices=FILTER_KIND_CHOICE, max_length=30, blank=False)
    value = models.CharField(_('value'), max_length=255, blank=False)
    objects = FilterEntryManager()
    
    def __unicode__(self):
        return u"{kind} from {user}".format(user=self.author.username, kind=self.get_kind_display())
    
    class Meta:
        verbose_name = _('user message filter')
        verbose_name_plural = _('user message filters')

class MessageManagerMixin(object):
    """
    Message manager enhanced with methods to follow a standardized backend
    """
    def get_backend(self, channel=None, author=None, last_id=None):
        """
        A all-in-one method to fetch messages with attempted behavior from a tribune 
        backend
        """
        q = self.from_chan(channel=channel)
        # Adds the user message filters
        q = q.bunkerize(author=author)
        # Ever force the right order to fetch
        q = q.orderize(last_id=last_id)
        return q
    
    def from_chan(self, channel=None):
        """Select messages only from default or given channel if any"""
        # TODO: clean option/argument to fetch messages from all channel (default and "real")
        # Default channel
        if not channel:
            return self.filter(channel__isnull=True)
        # Select on the specified channel or from the given channel ids
        else:
            if isinstance(channel, Channel):
                return self.filter(channel=channel)
            else:
                return self.filter(channel__slug=channel)
    
    def bunkerize(self, author=None):
        """Get message filters to excludes messages"""
        q = self.exclude()
        if author and author.is_authenticated():
            for x in author.filterentry_set.get_filters_args():
                q = q.exclude(**x)
        return q
    
    def orderize(self, last_id=None):
        """Desc ordering, optionnaly starting search from a ``last_id``"""
        if last_id:
            return self.filter(id__gt=last_id).order_by('-id')
        return self.order_by('-id')
    
    def last_id(self, last_id):
        """Limit the queryset to start his select from the given id"""
        return self.filter(id__gt=last_id)
    
    def flat(self):
        """Return only IDs, for debug purpose"""
        return self.values_list('id', flat=True)

# Need stuff to have manager chaining methods
class MessageQuerySet(QuerySet, MessageManagerMixin): pass
class MessageBackendManager(models.Manager, MessageManagerMixin):
    def get_query_set(self):
        return MessageQuerySet(self.model, using=self._db)

class Message(models.Model):
    """
    Message posted on tribune
    
    Message without Channel relation is on the default channel. The default channel is 
    not a Channel object, just the starting entry for the tribune.
    """
    channel = models.ForeignKey(Channel, verbose_name=_('channel'), blank=True, null=True, default=None)
    author = models.ForeignKey(User, verbose_name=_('identified author'), blank=True, null=True, default=None)
    created = models.DateTimeField(_('created date'), auto_now_add=True)
    clock = models.TimeField(_('clock'), auto_now_add=True)
    user_agent = models.CharField(_('User Agent'), max_length=70)
    ip = models.IPAddressField(_('IP adress'), blank=True, null=True)
    raw = models.TextField(_('raw'), blank=False)
    web_render = models.TextField(_('html'), blank=False)
    remote_render = models.TextField(_('xml'), blank=False)
    objects = MessageBackendManager()
    
    def __repr__(self):
        return "<Message: {id}>".format(id=self.id)
    
    def __unicode__(self):
        return self.raw
    
    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')
    
class Url(models.Model):
    """
    Url catched from a Message
    """
    message = models.ForeignKey(Message)
    author = models.ForeignKey(User, verbose_name=_('identified author'), blank=True, null=True, default=None)
    created = models.DateTimeField(_('created date'), blank=True)
    url = models.TextField(_('url'), blank=False)
    
    def __unicode__(self):
        return self.url
    
    def save(self, *args, **kwargs):
        if not self.created:
            self.author = self.message.author
            self.created = self.message.created
        super(Url, self).save(*args, **kwargs)
    
    class Meta:
        verbose_name = _('url')
        verbose_name_plural = _('urls')
