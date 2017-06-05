import pytest

from django.contrib.auth.models import User

from djangotribune.parser import GenericPostCleaner


@pytest.mark.parametrize('source_args,attempted', [
    (
        ('%H:%M:%S', 14, 15, 23),
        '14:15:23',
    ),
    # Clock part that are not ten is formatted on two digits
    (
        ('%H:%M:%S', 1, 2, 3),
        '01:02:03',
    ),

    (
        ('%H:%M:%S', 12, 0, 0),
        '12:00:00',
    ),
    (
        ('%H:%M:%S', 0, 0, 0),
        '00:00:00',
    ),
    # Clock format without second still have second appended
    (
        ('%H:%M', 14, 15, 23),
        '14:15:23',
    ),
    (
        ('%H:%M', 12, 0, 0),
        '12:00:00',
    ),
    (
        ('%H:%M', 0, 0, 0),
        '00:00:00',
    ),
    # Clock format with colon separator
    (
        ('%H%M%S', 14, 15, 23),
        '141523',
    ),
    (
        ('%H%M', 14, 15, 23),
        '141523',
    ),
    # Invalid clock time still be formatted
    (
        ('%H:%M:%S', 1, 75, 3),
        '01:75:03',
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
    # Correct clocks
    (
        """14:15:23 Yep 14:15:23 Nope""",
        ['14:15:23', ' Yep ', '14:15:23', ' Nope']
    ),
    # Invalid clocks are ignored
    (
        """14:75:20 Pim 14:15:200 Pom""",
        ['14:75:20 Pim 14:15:200 Pom']
    ),
    # Html in <code> are not interpreted nor corrected
    (
        """You may add a new <code><a><div/></a></code> in your element""",
        ['You may add a new ', '<code>', '<a><div/></a>', '</code>',
         ' in your element']
    ),
    # <code> in <code> has its closing tag swallowed
    (
        """Code in code <code><code><div/></code></code>""",
        ['Code in code ', '<code>', '<code>', '<div/>', '</code>']
    ),
    # Invalid html outside <code> are corrected
    (
        """Bim Bam <b><i>Boum</b>""",
        ['Bim Bam ', '<b>', '<i>', 'Boum', '</i>', '</b>']
    ),
    # HTML classname on recognized tag is assumed as text and its closing tag
    # is swallowed
    (
        """Bum Bam <b class="foo">Boum</b>""",
        ['Bum Bam <b class=', '"', 'foo', '"', '>Boum']
    ),
    # HTML classname and invalid HTML
    (
        """Bom Bam <b class="foo"><i>Boum</b>""",
        ['Bom Bam <b class=', '"', 'foo', '"', '>', '<i>', 'Boum']
    ),
    # Basic url
    (
        """Searching way through http://perdu.com""",
        ['Searching way through ', 'http://perdu.com']
    ),
    # Basic totoz
    (
        """First i was like [:totoz] then i was [:lovev]""",
        ['First i was like ', '[:totoz]', ' then i was ', '[:lovev]']
    ),
    # Basic moment
    (
        """<m>I'm here</m>""",
        ['<m>', "I'm here", '</m>']
    ),
])
def test_parse(source, attempted):
    """Parsing message source using basic 'post cleaner'"""
    gpc = GenericPostCleaner()
    gpc.append_batch(source)

    assert gpc == attempted
