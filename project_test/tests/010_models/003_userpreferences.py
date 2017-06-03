import pytest

from djangotribune.models import UserPreferences

from project_test.tests.factories import UserPreferencesFactory


@pytest.mark.django_db
def test_single_goods():
    """Single UserPreferences creation from factory"""
    factory_prefs = UserPreferencesFactory()

    assert UserPreferences.objects.count() == 1

    prefs = UserPreferences.objects.get(owner=factory_prefs.owner)
    assert prefs.smileys_host_url == prefs.smileys_host_url


@pytest.mark.django_db
def test_many_goods():
    """Multiple UserPreferences creation from factory"""
    for k in range(1, 6):
        factory_filter = UserPreferencesFactory()

    assert UserPreferences.objects.count() == 5
