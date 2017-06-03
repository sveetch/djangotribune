import pytest

from django.contrib.auth.models import User

from djangotribune.parser import XmlEntities


@pytest.mark.parametrize('source,attempted', [
    ("""Foo""", """Foo"""),
    ("""Lorem & ipsum""", """Lorem &#38; ipsum"""),
    ("""Lorem < ipsum""", """Lorem &#60; ipsum"""),
    ("""Lorem > ipsum""", """Lorem &#62; ipsum"""),
    ("""Lorem " ipsum""", """Lorem &#34; ipsum"""),
    ("""Lorem & "ipsum" nec & <div>""", """Lorem &#38; &#34;ipsum&#34; nec &#38; &#60;div&#62;"""),
])
def test_replacement(source, attempted):
    """Entity replacement"""
    assert XmlEntities(source) == attempted
