import io
import os
import sys
from urllib.parse import urljoin

import requests
from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup


class DataUploader(object):
    # urls
    base_url = "https://www.proveyourworth.net"
    test_url = urljoin(base_url, 'level3/')
    name_activation_url = urljoin(test_url, 'activate/')
    payload_image_url = urljoin(test_url, 'payload/')
    upload_url = urljoin(test_url, 'reaper/')


    def __init__(self):
        self.name = "Juan Garcia"
        self.email = "juan.garcia@gmail.com"
        self.cv_file = "resume.pdf"
        self.about = """Write your about here"""

        self.stateful_hash: str = ''
        self.cookie: str = ''

        self.latest_response: requests.Response = None
        """Stores the latest response obtained by a request"""

        self.is_name_active = False
        """Whether the user name/cookie combination has been activated"""


    def get_stateful_hash_and_cookie(self):
        self.latest_response = requests.get(self.test_url)

        self.cookie = self.latest_response.cookies.get('PHPSESSID')
        soup = BeautifulSoup(self.latest_response.text, features="html.parser")
        self.stateful_hash = soup.find('input', {'name': 'statefulhash'}).attrs['value']

        assert self.cookie and self.stateful_hash, "Couldn't obtain cookie or stateful hash"


    def activate_name(self):
        if not self.cookie:
            self.get_stateful_hash_and_cookie()

        params = {'username': self.name, 'statefulhash': self.stateful_hash}

        self.latest_response = requests.get(
            self.name_activation_url,
            params=params,
            headers=self._get_headers()
        )
        self.is_name_active = True


    def get_payload_image(self):
        if not self.is_name_active:
            self.activate_name()

        self.latest_response = requests.get(
            self.payload_image_url,
            headers=self._get_headers()
        )

        return Image.open(io.BytesIO(self.latest_response.content))


    def upload_data(self):
        im = self.get_payload_image()
        im = self.watermark_image(im, f"{self.name} {self.cookie}")
        image_name = 'image.jpg'
        im.save(image_name)

        text_fields = {
            'email': self.email,
            'name': self.name,
            'aboutme': self.about,
        }
        files = {
            'resume': (self.cv_file, open(self.cv_file, 'rb'), 'application/pdf'),
            'image': (image_name, open(image_name, 'rb'), 'image/jpg'),
            'code': (os.path.basename(__file__), open(__file__, 'r'), 'text/plain'),
        }

        headers = self._get_headers()
        formatted_name = self.name.replace(' ', '-')
        headers['User-Agent'] = f"X-{formatted_name}"

        self.latest_response = requests.post(
            self.upload_url, headers=headers, data=text_fields, files=files
        )


    @staticmethod
    def watermark_image(image: Image, text='watermark'):
        font = ImageFont.truetype('Cousine-Bold.ttf', 24)
        draw = ImageDraw.Draw(image)

        margin = 10
        draw.text((margin, margin), text, font=font)

        return image


    def _get_headers(self):
        return {
            'Cookie': f"PHPSESSID={self.cookie}",
        }
