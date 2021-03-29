"""
Instructions to use:


"""
import io
import os
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
        self.about = """Write your about here"""

        self.cv_file = "resume.pdf"
        self.image_file = 'image.jpg'

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
        im.save(self.image_file)

        text_fields = {
            'email': self.email,
            'name': self.name,
            'aboutme': self.about,
        }
        files = {
            'resume': (self.cv_file, open(self.cv_file, 'rb'), 'application/pdf'),
            'image': (self.image_file, open(self.image_file, 'rb'), 'image/jpg'),
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


if __name__ == "__main__":
    uploader = DataUploader()

    uploader.name = "Armando Rivero"
    uploader.email = "armando.rivero143@gmail.com"
    uploader.about = """
    Well, I have a hard time talking of myself. To be honest, I'm not sure if you should be hiring me.
    I mean, I don't have much solid, full-time experience. What I do have, on the other hand,
    it's a lot of love for programming and for code, an almost obsessive desire to create great code
    that can act as the long term foundation for a successful organization. That, and a equal burning passion
    for learning new programming stuff. I like to believe that, since I love learning so much, I'm kind of good at it.
    
    I have my weaknesses for sure. I'm a bit slow, since I prefer to do things carefully. I get bored if I
    have to do the same thing over and over. My spirit falls if I have to multitask for too long. 
    I prefer doing focused, high quality work instead. I'd love to correct the worst weaknesses
    I can see and the others I'm surely missing and would be forever grateful for any guidance in that regard. 
    
    To summarize, if you want somebody that will grow with you, that you can ask to try new ideas and technologies, 
    I could be your guy. If you want a generalist, that knows a bit about many things and will try to learn
    about what your organization does out of pure curiosity, that could be me. If, instead,
    you want somebody fast from day zero, that you could plug like a piece of machinery to perform the same
    kind of work forever, I'd probably not recommend hiring myself.  
    
    Thanks for listening to the rant :) 
    """

    uploader.upload_data()
