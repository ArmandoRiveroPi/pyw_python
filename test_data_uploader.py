import imghdr
import re

import pytest

from data_uploader import DataUploader
from PIL import Image
import os

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

@pytest.mark.integration
def test_get_payload_image():
    uploader = DataUploader()

    image_name = 'test_file_image.jpg'
    uploader.get_payload_image(image_name)
    im = Image.open(image_name)

    assert imghdr.what(image_name) == 'jpeg'

    im.close()
    os.unlink(image_name)
