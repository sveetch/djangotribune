import random

import factory

from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from djangotribune.models import (Channel, UserPreferences, FilterEntry,
                                  Message)


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory for User model
    """
    first_name = factory.Sequence(lambda n: 'Firstname {0}'.format(n))
    last_name = factory.Sequence(lambda n: 'Lastname {0}'.format(n))
    username = factory.LazyAttribute(lambda obj: '{0}.{1}'.format(obj.first_name.lower().replace(' ', '_'), obj.last_name.lower().replace(' ', '_')))
    email = factory.LazyAttribute(lambda obj: '{0}.{1}@example.com'.format(obj.first_name.lower().replace(' ', '_'), obj.last_name.lower().replace(' ', '_')))

    password = factory.PostGenerationMethodCall('set_password', 'adm1n')

    is_superuser = False
    is_staff = False
    is_active = True

    class Meta:
        model = User


class ChannelFactory(factory.django.DjangoModelFactory):
    """
    Factory for User model
    """
    title = factory.Sequence(lambda n: 'Channel {0}'.format(n))
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = Channel


class UserPreferencesFactory(factory.django.DjangoModelFactory):
    """
    Factory for User model
    """
    owner = factory.SubFactory(UserFactory)
    refresh_time = factory.Iterator([5000, 1000, 10000])
    refresh_actived = factory.Iterator([True, False])
    smileys_host_url = factory.Iterator(['http://totoz.eu', 'http://nsfw.totoz.eu'])

    class Meta:
        model = UserPreferences


class FilterEntryFactory(factory.django.DjangoModelFactory):
    """
    Factory for FilterEntry model
    """
    owner = factory.SubFactory(UserFactory)
    target = factory.Iterator([item[0]
                               for item in FilterEntry.FILTER_TARGET_CHOICE])
    kind = factory.Iterator([item[0]
                             for item in FilterEntry.FILTER_KIND_CHOICE])

    # 'value' field is lazy because content (username, ua, message pattern)
    # depends from target field value
    @factory.lazy_attribute
    def value(self):
        if self.target == 'user_agent':
            return factory.Faker('user_agent')
        elif self.target == 'owner__username':
            return factory.Faker('user_name')
        else:
            return factory.Faker('text', max_nb_chars=200)

    class Meta:
        model = FilterEntry


class MessageFactory(factory.django.DjangoModelFactory):
    """
    Factory for Message model

    Many things (clock, web/xml rendered msg) are correctly filled from
    form+parser, not directly within model, should we do it inside model save??
    """
    channel = None # Use default channel, tests will specify it when needed
    owner = factory.SubFactory(UserFactory)
    user_agent = factory.Faker('user_agent')
    ip = factory.Faker('ipv4', network=False)
    # TODO: raw should use a custom faker using lorem and adding some markup
    #       (valid and invalid)
    raw = factory.Faker('text', max_nb_chars=200)
    # TODO: 'web_render' and 'remote_render' should be LazyAttribute using
    #       parsed 'raw' value to be valid BML (Bouchot Markup Language)
    #       according to their format
    web_render = factory.LazyAttribute(lambda obj: obj.raw)
    remote_render = factory.LazyAttribute(lambda obj: obj.raw)

    class Meta:
        model = Message
