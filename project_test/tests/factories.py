import random

import factory

from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify

from djangotribune.models import Channel, UserPreferences


class UserFactory(factory.django.DjangoModelFactory):
    """
    Simple factory for User model
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
    Simple factory for User model
    """
    title = factory.Sequence(lambda n: 'Channel {0}'.format(n))
    slug = factory.LazyAttribute(lambda obj: slugify(obj))

    class Meta:
        model = Channel


class UserPreferencesFactory(factory.django.DjangoModelFactory):
    """
    Simple factory for User model
    """
    owner = factory.SubFactory(UserFactory)
    refresh_time = factory.Iterator([5000, 1000, 10000])
    refresh_actived = factory.Iterator([True, False])
    smileys_host_url = factory.Iterator(['http://totoz.eu', 'http://nsfw.totoz.eu'])

    class Meta:
        model = UserPreferences
