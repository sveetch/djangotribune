import pytest

from django.contrib.auth.models import User

from project_test.tests.factories import UserFactory


@pytest.mark.django_db
def test_single_goods():
    """Single User creation from factory"""
    factory_user = UserFactory()

    assert User.objects.count() == 1

    u = User.objects.get(username=factory_user.username)
    assert u.email == factory_user.email
