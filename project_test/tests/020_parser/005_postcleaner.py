from __future__ import unicode_literals

import pytest

from django.contrib.auth.models import User

from djangotribune.parser import PostCleaner


@pytest.mark.parametrize('source,attempted', [
    (
        """Foo""",
        ["""Foo"""]
    ),
    # Correct clocks
    (
        """14:15:23 Yep 14:15:23 Nope""",
        ['<clock time="141523">', '14:15:23', '</clock>', ' Yep ',
         '<clock time="141523">', '14:15:23', '</clock>', ' Nope']
    ),
    # Invalid clocks are ignored
    (
        """14:75:20 Pim 14:15:200 Pom""",
        ['14:75:20 Pim 14:15:200 Pom']
    ),
    # Html in <code> are not interpreted nor corrected
    (
        """You may add a new <code><a><div/></a></code> in your element""",
        ['You may add a new ', '<code>',
         '&#60;a&#62;&#60;div/&#62;&#60;/a&#62;', '</code>',
         ' in your element']
    ),
    # <code> in <code> has its closing tag swallowed
    (
        """Code in code <code><code><div/></code></code>""",
        ['Code in code ', '<code>', '&#60;code&#62;', '&#60;div/&#62;',
         '</code>']
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
        ['Bum Bam &#60;b class=', '"', 'foo', '"', '&#62;Boum']
    ),
    # HTML classname and invalid HTML
    (
        """Bom Bam <b class="foo"><i>Boum</b>""",
        ['Bom Bam &#60;b class=', '"', 'foo', '"', '&#62;', '<i>', 'Boum']
    ),
    # Basic url
    (
        """Searching way through http://perdu.com""",
        ['Searching way through ', '<a href="', 'http://perdu.com',
         '"$DummyToken$>', '[url]', '</a>']
    ),
    # Basic totoz
    (
        """First i was like [:totoz] then i was [:lovev]""",
        ['First i was like ', '<totoz name="totoz"/>', ' then i was ',
         '<totoz name="lovev"/>']
    ),
    # Basic moment
    (
        """<m>I'm here</m>""",
        ['<m>', "I'm here", '</m>']
    ),
])
def test_parse(source, attempted):
    """Parsing message source using spost cleaner'"""
    dummy_token = "$DummyToken$"
    gpc = PostCleaner(escape_token=dummy_token)
    gpc.append_batch(source)

    assert gpc == attempted


@pytest.mark.parametrize('source,attempted', [
    (
        'No clock',
        []
    ),
    (
        '12:12',
        ['12:12']
    ),
    (
        '12:12:12',
        ['12:12:12']
    ),
    (
        '141523',
        ['141523']
    ),
    (
        '01:75:03',
        []
    ),
    # Correct clocks
    (
        '14:15:23 Yep 14:15:23 Nope',
        ['14:15:23', '14:15:23']
    ),
    # Invalid clocks are ignored
    (
        '14:75:20 Pim 14:15:200 Pom',
        []
    ),
    # Clock with a date, date is ignored
    (
        '2008/28/03#21:42:42 Fim fam foom',
        ['21:42:42']
    ),
    # Mixed clocks
    (
        '12:12:12 141523 16:15 01:75:03',
        ['12:12:12', '141523', '16:15']
    ),
])
def test_clocks(source, attempted):
    """Stored recognized clocks"""
    gpc = PostCleaner()
    gpc.append_batch(source)

    assert gpc.matched_clocks == attempted


@pytest.mark.parametrize('source,attempted', [
    (
        'No totoz',
        []
    ),
    (
        '[:totoz]',
        ['totoz']
    ),
    (
        '[:flu12]',
        ['flu12']
    ),
    (
        '[:totoz-foo]',
        ['totoz-foo']
    ),
    (
        '[:totoz:1]',
        ['totoz:1']
    ),
    (
        '[:totoz]]',
        ['totoz']
    ),
    (
        '[:totoz including some spaces]',
        ['totoz including some spaces']
    ),
    (
        'First i was like [:totoz] then i was [:lovev]',
        ['totoz', 'lovev']
    ),
    (
        u'[:téléphone]',
        []
    ),
    (
        u'[:totoz²]',
        []
    ),
    (
        '[:totoz;1]',
        []
    ),
    (
        '[:totoz<]',
        []
    ),
    (
        '[:totoz>]',
        []
    ),
    (
        '[:[totoz]',
        []
    ),
])
def test_totozs(source, attempted):
    """Stored recognized totoz"""
    gpc = PostCleaner()
    gpc.append_batch(source)

    assert gpc.matched_totozs == attempted


@pytest.mark.parametrize('source,attempted', [
    (
        'No url',
        []
    ),
    (
        'http://perdu.com',
        ['http://perdu.com']
    ),
    (
        'http://',
        ['http://']
    ),
    (
        u'http://fr.wikipedia.org/wiki/Téléphone',
        [u'http://fr.wikipedia.org/wiki/Téléphone']
    ),
    (
        u'http://fr.finance.yahoo.com/q/bc?s=^FCHI&t=1y&l=on&z=m&q=l&c=',
        [u'http://fr.finance.yahoo.com/q/bc?s=^FCHI&t=1y&l=on&z=m&q=l&c=']
    ),
    (
        'gopher://gopher.floodgap.com/0/fun/figletgw?kupo!|font=isometric3',
        ['gopher://gopher.floodgap.com/0/fun/figletgw?kupo!|font=isometric3']
    ),
    (
        'http://192.168.0.101:8888/about/',
        ['http://192.168.0.101:8888/about/']
    ),
    (
        ('http://www.marktplaats.nl/index.php?url=http%3A//kopen.marktplaats.'
         'nl/woningen-koop/buitenland/c1041.html%3Fxl%3D1%26ds%3Dto%253A1%253'
         'Bpu%253A0%253Bl1%253A1032%253Bl2%253A1041%253Bpa%253A150000%253Bdi%'
         '253A%253Blt%253Azip%253Bsfds%253A%253Bpt%253A0%253Bmp%253Anumeric%2'
         '53Bosi%253A2%26ppu%3D0%26aw%255B68%255D%255B0%255D%3D448%26p%3D1%26'
         'av%5B-1%5D%5B0%5D%3D0'),
        [('http://www.marktplaats.nl/index.php?url=http%3A//kopen.marktplaats.'
         'nl/woningen-koop/buitenland/c1041.html%3Fxl%3D1%26ds%3Dto%253A1%253'
         'Bpu%253A0%253Bl1%253A1032%253Bl2%253A1041%253Bpa%253A150000%253Bdi%'
         '253A%253Blt%253Azip%253Bsfds%253A%253Bpt%253A0%253Bmp%253Anumeric%2'
         '53Bosi%253A2%26ppu%3D0%26aw%255B68%255D%255B0%255D%3D448%26p%3D1%26'
         'av%5B-1%5D%5B0%5D%3D0')]
    ),
    (
        ('http://www.none.fr/search?hl=fr&btnG=Recherche+Google&meta=&q=azeda'
         'ed-'),
        [('http://www.none.fr/search?hl=fr&btnG=Recherche+Google&meta=&q=azeda'
         'ed-')]
    ),
])
def test_urls(source, attempted):
    """Stored recognized urls"""
    gpc = PostCleaner()
    gpc.append_batch(source)

    assert gpc.matched_urls == attempted
