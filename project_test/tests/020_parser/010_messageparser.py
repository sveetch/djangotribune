from __future__ import unicode_literals

from datetime import datetime, timedelta

import pytest

from django.contrib.auth.models import User

from djangotribune.parser import MessageParser

from project_test.tests.gip_samples import REMOTE_SAMPLES, WEB_SAMPLES


@pytest.mark.parametrize('source,attempted', REMOTE_SAMPLES)
def test_remote_parse(source, attempted):
    mp = MessageParser()

    result = mp.render(source)

    assert result['remote_render'] == attempted
