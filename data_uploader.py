import io
from urllib.parse import urljoin

import requests
from PIL import Image
from bs4 import BeautifulSoup


class DataUploader(object):
    name = "Juan Garcia"
    email = "juan.garcia@gmail.com"
    cv_file = "resume.pdf"
    about = """Write your about here"""
    # urls
    base_url = "https://www.proveyourworth.net"
    test_url = urljoin(base_url, 'level3/')
    name_activation_url = urljoin(test_url, 'activate/')
    payload_image_url = urljoin(test_url, 'payload/')


    def __init__(self):
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
            headers=self._get_cookie_headers()
        )
        self.is_name_active = True


    def get_payload_image(self, image_name='test.jpg'):
        if not self.is_name_active:
            self.activate_name()

        self.latest_response = requests.get(
            self.payload_image_url,
            headers=self._get_cookie_headers()
        )

        im = Image.open(io.BytesIO(self.latest_response.content))
        im.save(image_name)
        im.close()


    def _get_cookie_headers(self):
        return {'Cookie': f"PHPSESSID={self.cookie}"}
