"""
Defines an abstract class for webcomics
"""


import abc

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
        path = Path(path)
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
    def alt_url(self):
        """url for alt text"""
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

    @abc.abstractmethod
    def download(self, folder, output_file):
        """download the picture as `output_file` inside `folder`"""
        return None

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
