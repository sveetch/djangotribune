# -*- coding: utf-8 -*-
"""
Data Models
"""
import datetime, pytz

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import utc

from django.contrib.auth.models import User


# Aliases for target field names
FILTER_TARGET_ALIASES = (
    ('ua', 'user_agent'),
    ('owner', 'owner__username'),
    ('message', 'raw'),
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
    Channel board reference
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
    User preferences for board usage
    """
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(_('created date'), auto_now_add=True)
    refresh_time = models.IntegerField(_('refresh time'),
                                       blank=False, default=5000)
    refresh_actived = models.BooleanField(_('refresh actived'), default=True)
    smileys_host_url = models.CharField(_('smileys host url'),
                                        max_length=150, blank=False)

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
        selectors = ['target', 'value', 'kind']
        for item in self.get_query_set().all().values(*selectors):
            key = "{target}__{kindfunc}".format(target=item['target'],
                                                kindfunc=item['kind'])
            args.append( {key: item['value']} )
        return tuple(args)

    def get_filters(self):
        """Return filters as a tuple of tuples (target, pattern, kind)"""
        args = []
        selectors = ['target', 'value', 'kind']
        for item in self.get_query_set().all().values(*selectors):
            args.append( (item['target'], item['value'], item['kind']) )
        return tuple(args)


class FilterEntry(models.Model):
    """
    Personnal user entry to hide messages
    """
    # Target determines wich field is used on the filter
    FILTER_TARGET_CHOICE = (
        ('user_agent', _('User Agent')),
        ('owner__username', _('Username')),
        ('raw', _('Raw message')),
    )

    # Kind determines what kind of Field lookup is used on the filter.
    # 'regex' are disabled because they seem to have too much cost on
    # performance
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

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=False)
    target = models.CharField(_('target'), choices=FILTER_TARGET_CHOICE,
                              max_length=30, blank=False)
    kind = models.CharField(_('kind'), choices=FILTER_KIND_CHOICE,
                            max_length=30, blank=False)
    # value can be related to any field respecting 'FILTER_TARGET_CHOICE'
    value = models.CharField(_('value'), max_length=255, blank=False)
    objects = FilterEntryManager()

    def __unicode__(self):
        return u"{kind} from {user}".format(user=self.owner.username,
                                            kind=self.get_kind_display())

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
        # TODO: add a new option/argument to fetch messages from all channel
        # (default and "reals")
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

    def bunkerize(self, owner=None):
        """
        Get message filters to excludes messages

        This is method automatically get the saved filters in the owner
        profile in database.
        """
        q = self.exclude()
        if owner and owner.is_authenticated():
            for x in owner.filterentry_set.get_filters_kwargs():
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

    Message without Channel relation is on the default channel. The default
    channel is not a Channel object, just the starting entry for the tribune.

    The clock attribute is filled from the created attribute, and its purpose
    is mainly for some specific queryset filters.
    """
    channel = models.ForeignKey('Channel', verbose_name=_('channel'),
                                blank=True, null=True, default=None)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                               blank=True, null=True, default=None)
    created = models.DateTimeField(_('created date'))
    clock = models.TimeField(_('clock'), blank=True)
    user_agent = models.CharField(_('User Agent'), max_length=150)
    ip = models.GenericIPAddressField(_('IP adress'), blank=True, null=True)
    raw = models.TextField(_('raw'), blank=False)
    web_render = models.TextField(_('html'), blank=False)
    remote_render = models.TextField(_('xml'), blank=False)
    objects = MessageBackendManager()

    def __repr__(self):
        return "<Message: {id}>".format(id=self.id)

    def __unicode__(self):
        return "{date} by {owner}".format(date=self.created,
                                           owner=self.get_identity())

    def get_created_date(self):
        return self.created.date()

    def get_identity(self):
        if not self.owner:
            return self.user_agent[:50]
        return self.owner

    def save(self, *args, **kwargs):
        # 'created' field should be filled from posting form (to have a sooner
        # datetime without to wait for model save) but in case message entry
        # is created out of the form process, automatically fill it here
        if not self.created:
            self.created = datetime.datetime.utcnow().replace(tzinfo=utc)

        # Allways fill 'clock' field from 'created' field
        tz = pytz.timezone(settings.TIME_ZONE)
        self.clock = self.created.astimezone(tz).time()

        super(Message, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('message')
        verbose_name_plural = _('messages')


class Url(models.Model):
    """
    Url catched from a Message
    """
    message = models.ForeignKey('Message')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                               blank=True, null=True, default=None)
    created = models.DateTimeField(_('created date'), blank=True)
    url = models.TextField(_('url'), blank=False)

    def __unicode__(self):
        return self.url

    def save(self, *args, **kwargs):
        # Inherit owner and created from related message
        if not self.created:
            self.created = self.message.created
        if not self.owner:
            self.owner = self.message.owner
        super(Url, self).save(*args, **kwargs)

    class Meta:
        verbose_name = _('url')
        verbose_name_plural = _('urls')
