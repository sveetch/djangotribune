import pytest

from djangotribune.models import FilterEntry

from .factories import FilterEntryFactory


@pytest.mark.django_db
def test_single_goods():
    """Single FilterEntry creation from factory"""
    factory_filter = FilterEntryFactory()

    assert FilterEntry.objects.count() == 1

    prefs = FilterEntry.objects.get(owner=factory_filter.owner)
    assert prefs.value == prefs.value
