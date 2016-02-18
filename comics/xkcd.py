"""Defines a class for xkcd webcomics
"""

import json

import requests

from .webcomic import WebComic


class XKCDComic(WebComic):
    """Class to describe XKCD Comics"""

    BASE_URL = 'http://www.xkcd.com/'
    BASE_IMG_URL = 'http://imgs.xkcd.com/comics/'
    destination_folder = None

    @staticmethod
    def latest_id():
        """Return the uid of the latest comic in the collection"""
        req = requests.get('http://xkcd.com/info.0.json')
        num = json.loads(req.content.decode())['num']
        return num

    @staticmethod
    def first_id():
        """Return the uid of the first comic in the collection"""
        return 1

    @classmethod
    def all(cls):
        """return an iterable of all the currently
        available comics form this collection """
        return [XKCDComic(num) for num in range(1, cls.latest_id() + 1)]

    def __init__(self, number):
        """Make a WebComic object"""
        super().__init__(number)
        self.uid = number
        self.data = ''

    def __str__(self):
        return "XKCD Webcomic {}: {}".format(self.number, self.title)

    def __repr__(self):
        return str(self)

    def ensure_data(self):
        """Make sure the data is downloaded if necessary"""
        if self.data:
            return
        link = self.BASE_URL + str(self.number)
        req = requests.get(link + '/info.0.json', timeout=10)
        self.data = json.loads(req.content.decode())

    @property
    def alt_text(self):
        """The alt text for this comic, or an empty string"""
        self.ensure_data()
        return self.data['alt']

    @property
    def image_url(self):
        """url of hosted image"""
        self.ensure_data()
        return self.data['img']

    @property
    def title(self):
        """title of this comic"""
        self.ensure_data()
        return self.data['safe_title']

    @property
    def utitle(self):
        """title of this comic, with number. Suitable to sort"""
        return '{:>04}-{}'.format(self.number, self.title)

    @property
    def filename(self):
        """The candidate filename for this comics image"""
        imgname = self.image_url.replace(self.BASE_IMG_URL, '')
        return '{:>04}-{}'.format(self.number, imgname)
