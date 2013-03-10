# -*- coding: utf-8 -*-
"""
Data Models
"""
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import User

# Target determines wich field is used on the filter
FILTER_TARGET_CHOICE = (
    ('user_agent', _('User Agent')),
    ('author__username', _('Username')),
    ('raw', _('Raw message')),
)
# Aliases for target field names
FILTER_TARGET_ALIASES = (
    ('ua', 'user_agent'),
    ('author', 'author__username'),
    ('message', 'raw'),
)
# Kind determines what kind of Field lookup is used on the filter.
# 'regex' are disabled because they seem to have too much cost on performance
FILTER_KIND_CHOICE = (
    #('regex', _('Case-sensitive regular expression match')),
    #('iregex', _('Case-insensitive regular expression match')),
    ('contains', _('Case-sensitive containment test')),
    ('icontains', _('Case-insensitive containment test')),
    ('exact', _('Case-sensitive exact match')),
    ('iexact', _('Case-insensitive exact match')),
    ('startswith', _('Case-sensitive starts-with')),
    ('endswith', _('Case-sensitive ends-with')),
)
# Aliases for lookup kinds
FILTER_KIND_ALIASES = (
    ('*=', 'contains'),
    ('|=', 'icontains'),
    ('==', 'exact'),
    ('~=', 'iexact'),
    ('^=', 'startswith'),
    ('$=', 'endswith'),
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
    def get_filters_kwargs(self):
        """Return filters as a tuple of dicts kwargs"""
        args = []
        for item in self.get_query_set().all().values('target', 'value', 'kind'):
            key = "{target}__{kindfunc}".format(target=item['target'], kindfunc=item['kind'])
            args.append( {key: item['value']} )
        return tuple(args)

    def get_filters(self):
        """Return filters as a tuple of tuples (target, pattern, kind)"""
        args = []
        for item in self.get_query_set().all().values('target', 'value', 'kind'):
            args.append( (item['target'], item['value'], item['kind']) )
        return tuple(args)

class FilterEntry(models.Model):
    """
    Personnal user entry to hide messages
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
    def get_backend(self, channel=None, filters=None, last_id=None):
        """
        A all-in-one method to fetch messages with all attempted behaviors from 
        a tribune backend
        """
        q = self.from_chan(channel=channel)
        # Add the user message filters if any
        if filters:
            q = q.apply_filters(filters)
        # Ever force the right order to fetch
        q = q.orderize(last_id=last_id)
        return q
    
    def from_chan(self, channel=None):
        """Select messages only from default or given channel if any"""
        # TODO: add a new option/argument to fetch messages from all channel (default 
        # and "reals")
        # Default channel
        if not channel:
            return self.filter(channel__isnull=True)
        # Select on the specified channel or from the given channel ids
        else:
            if isinstance(channel, Channel):
                return self.filter(channel=channel)
            else:
                return self.filter(channel__slug=channel)
    
    def apply_filters(self, filters):
        """
        Apply messages filtering from the given filters
        
        This is exclude filters only, used to exclude some messages
        
        Filters are tuple (target, pattern, kind)
        """
        q = self.exclude()
        args = []
        for v in filters:
            target, pattern, kind = v
            key = "{target}__{kindfunc}".format(target=target, kindfunc=kind)
            q = q.exclude(**{key: pattern})
        return q
    
    def bunkerize(self, author=None):
        """
        Get message filters to excludes messages
        
        This is method automatically get the saved filters in the author profile in 
        database.
        """
        q = self.exclude()
        if author and author.is_authenticated():
            for x in author.filterentry_set.get_filters_kwargs():
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

# Needed stuff to have manager chaining methods
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
    user_agent = models.CharField(_('User Agent'), max_length=150)
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
