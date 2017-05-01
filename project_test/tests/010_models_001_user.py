import pytest

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from .factories import UserFactory


@pytest.mark.django_db
def test_factory_user():
    """Dummy user creation from factory"""
    factory_user = UserFactory()

    assert User.objects.count() == 1

    u = User.objects.get(username=factory_user.username)
    assert u.email == factory_user.email
