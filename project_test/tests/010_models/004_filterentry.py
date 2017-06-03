import pytest

from djangotribune.models import FilterEntry

from project_test.tests.factories import FilterEntryFactory


@pytest.mark.django_db
def test_single_goods():
    """Single FilterEntry creation from factory"""
    factory_filter = FilterEntryFactory()

    assert FilterEntry.objects.count() == 1

    prefs = FilterEntry.objects.get(owner=factory_filter.owner)
    assert prefs.value == prefs.value


@pytest.mark.django_db
def test_many_goods():
    """Multiple FilterEntry creation from factory"""
    for k in range(1, 6):
        factory_filter = FilterEntryFactory()

    assert FilterEntry.objects.count() == 5
