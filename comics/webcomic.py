"""
Defines an abstract class for webcomics
"""


import abc

import requests

from path import Path


class WebComic(metaclass=abc.ABCMeta):
    """Class for webcomics"""

    @staticmethod
    @abc.abstractmethod
    def latest_id():
        """Return the uid of the latest comic in the collection"""

    @staticmethod
    @abc.abstractmethod
    def first_id():
        """Return the uid of the first comic in the collection"""

    @classmethod
    @abc.abstractmethod
    def all(cls):
        """
        return an iterable of all the currently
        available comics form this collection
        """

    @classmethod
    def set_destination(cls, path):
        """register this path as the destination for upcoming downloads"""
        path = Path(path).expand().abspath()
        if not path.isdir():
            path.makedirs()
        cls.destination_folder = path

    @abc.abstractmethod
    def __init__(self, number):
        """Make a WebComic object"""
        self.number = number

    @abc.abstractmethod
    def __str__(self):
        return "Webcomic"

    @abc.abstractmethod
    def __repr__(self):
        return "Webcomic"

    @property
    @abc.abstractmethod
    def alt_text(self):
        """The alt text for this comic, or an empty string"""
        return 'Alternative text'

    @property
    @abc.abstractmethod
    def image_url(self):
        """url of hosted image"""
        return 'http://www.example.com/'

    @property
    @abc.abstractmethod
    def title(self):
        """title of this comic"""
        return "Placeholder title"

    @property
    def utitle(self):
        """title of this comic, with number. Suitable to sort"""
        return '{:>04}-{}'.format(self.number, self.title)

    def download(self):
        """download the picture"""
        if self.destination_folder is None:
            # quick abort download if destination was never set
            return None
        if not self.has_target(self.destination_folder):
            return
        src = requests.get(self.image_url, timeout=10)
        if src.status_code == 404 or src.status_code != 200:
            src.close()
            return  # missing or network error or whatever
        with open(self.destination_folder.joinpath(self.filename), 'wb') as dest:
            dest.write(src.content)
        src.close()
        if self.alt_text:
            with open(self.destination_folder.joinpath(self.filename) + '.txt', 'w') as dest:
                dest.write(self.alt_text)
        return self.destination_folder.joinpath(self.filename)

    @property
    @abc.abstractmethod
    def filename(self):
        """The candidate filename for this comics image"""

    def has_target(self, folder):
        """true if this comic can be downloaded to `output_file` inside `folder`"""
        target = Path(folder).joinpath(self.filename)
        if target.isfile():
            return False
        return True
