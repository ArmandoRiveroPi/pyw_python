import imghdr
import os
import re

import pytest

from pyw_uploader import PywUploader


@pytest.mark.integration
def test_upload_data():
    uploader = PywUploader()

    uploader.get_stateful_hash_and_cookie()

    assert re.match(r'\w{32}', uploader.stateful_hash), "Wrong stateful hash format"
    assert re.match(r'\w{26}', uploader.cookie), "Wrong Cookie format"
    assert uploader.latest_response.url == uploader.test_url

    uploader.activate_name()

    assert 'Download the payload. Sign it with your name' in uploader.latest_response.text, "Couldn't activate"

    im = uploader.get_payload_image()
    im = uploader.watermark_image(im, 'some silly watermark')

    image_name = 'test_file_image.jpg'
    im.save(image_name)

    assert imghdr.what(image_name) == 'jpeg', "Couldn't save watermarked image"

    im.close()
    os.unlink(image_name)

    uploader.upload_data()

    headers = uploader.latest_response.headers

    assert headers.get('x-nice-work') == 'Pro.', "Couldn't submit test correctly"
