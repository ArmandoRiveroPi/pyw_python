import re

import pytest

from data_uploader import DataUploader


@pytest.mark.integration
def test_get_state_information():
    uploader = DataUploader()
    uploader.get_stateful_hash_and_cookie()

    assert re.match(r'\w{32}', uploader.stateful_hash)
    assert re.match(r'\w{26}', uploader.cookie)
    assert uploader.latest_response.url == uploader.test_url

@pytest.mark.integration
def test_activate_name():
    uploader = DataUploader()
    uploader.activate_name()

    assert 'Download the payload. Sign it with your name' in uploader.latest_response.text
