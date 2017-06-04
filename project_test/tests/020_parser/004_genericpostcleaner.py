import pytest

from django.contrib.auth.models import User

from djangotribune.parser import GenericPostCleaner


@pytest.mark.parametrize('source_args,attempted', [
    (
        ('%H:%M:%S', 14, 15, 23),
        '14:15:23',
    ),
    (
        ('%H:%M', 14, 15, 23),
        '14:15:23',
    ),
    (
        ('%H:%M:%S', 1, 2, 3),
        '01:02:03',
    ),
    (
        ('%H:%M:%S', 1, 75, 3),
        '01:75:03',
    ),
    (
        ('%H%M%S', 14, 15, 23),
        '141523',
    ),
    (
        ('%H%M', 14, 15, 23),
        '141523',
    ),
    (
        ('%H:%M:%S', 12, 0, 0),
        '12:00:00',
    ),
    (
        ('%H:%M', 12, 0, 0),
        '12:00:00',
    ),
    (
        ('%H:%M:%S', 0, 0, 0),
        '00:00:00',
    ),
    (
        ('%H:%M', 0, 0, 0),
        '00:00:00',
    ),
])
def test_format_clock(source_args, attempted):
    """Entity replacement"""
    gpc = GenericPostCleaner()
    assert gpc.format_clock(*source_args) == attempted


@pytest.mark.parametrize('source,attempted', [
    (
        """Foo""",
        ["""Foo"""]
    ),
    (
        """14:15:23 Yep 14:15:23 Nope""",
        ['14:15:23', ' Yep ', '14:15:23', ' Nope']
    ),
    (
        """You may add a new <code><div/></code> in your element""",
        ['You may add a new ', '<code>', '<div/>', '</code>',
         ' in your element']
    ),
    (
        """Searching way through http://perdu.com""",
        ['Searching way through ', 'http://perdu.com']
    ),
    (
        """First i was like [:totoz] then i was [:lovev]""",
        ['First i was like ', '[:totoz]', ' then i was ', '[:lovev]']
    ),
])
def test_parse(source, attempted):
    """Parsing message source using basic 'post cleaner'"""
    gpc = GenericPostCleaner()
    gpc.append_batch(source)
    assert gpc == attempted
