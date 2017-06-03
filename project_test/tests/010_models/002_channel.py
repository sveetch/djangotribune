import pytest

from djangotribune.models import Channel

from project_test.tests.factories import ChannelFactory


@pytest.mark.django_db
def test_single_goods():
    """Single Channel creation from factory"""
    factory_channel = ChannelFactory()

    assert Channel.objects.count() == 1

    u = Channel.objects.get(slug=factory_channel.slug)
    assert u.title == factory_channel.title


@pytest.mark.django_db
def test_many_goods():
    """Multiple Channel creation from factory"""
    for k in range(1, 6):
        factory_filter = ChannelFactory()

    assert Channel.objects.count() == 5
