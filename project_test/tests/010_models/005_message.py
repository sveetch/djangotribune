import pytest
import pytz

from djangotribune.models import Message

from project_test.tests.factories import MessageFactory


@pytest.mark.django_db
def test_single_goods(settings):
    """Single Message creation from factory"""
    factory_message = MessageFactory()

    assert Message.objects.count() == 1

    msg = Message.objects.get(owner=factory_message.owner)
    assert msg.raw == factory_message.raw

    tz = pytz.timezone(settings.TIME_ZONE)
    assert msg.clock == msg.created.astimezone(tz).time()


@pytest.mark.django_db
def test_many_goods():
    """Multiple UserPreferences creation from factory"""
    for k in range(1, 6):
        factory_filter = MessageFactory()

    assert Message.objects.count() == 5
