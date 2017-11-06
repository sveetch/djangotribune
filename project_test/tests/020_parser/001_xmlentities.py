import pytest

from django.contrib.auth.models import User

from djangotribune.parser import XmlEntities


@pytest.mark.parametrize('source,attempted', [
    ("""Foo""", """Foo"""),
    ("""Lorem & ipsum""", """Lorem &amp; ipsum"""),
    ("""Lorem < ipsum""", """Lorem &lt; ipsum"""),
    ("""Lorem > ipsum""", """Lorem &gt; ipsum"""),
    ("""Lorem " ipsum""", """Lorem &quot; ipsum"""),
    ("""Lorem & "ipsum" nec & <div>""", """Lorem &amp; &quot;ipsum&quot; nec &amp; &lt;div&gt;"""),
])
def test_replacement(source, attempted):
    """Entity replacement"""
    assert XmlEntities(source) == attempted
