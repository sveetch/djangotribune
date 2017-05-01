import random

import factory

from django.conf import settings
from django.contrib.auth.models import User


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
