from __future__ import unicode_literals

from datetime import datetime, timedelta

import pytest

from django.contrib.auth.models import User

from djangotribune.parser import MessageParser

from project_test.tests.gip_samples import SAMPLES


@pytest.mark.parametrize('source,attempted', SAMPLES)
def test_parse(source, attempted):
    mp = MessageParser()

    result = mp.render(source)

    assert result['remote_render'] == attempted
