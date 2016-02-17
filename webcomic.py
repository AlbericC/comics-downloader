
"""
Defines classes for webcomics
"""


import abc


class WebComic(metaclass=abc.ABCMeta):
    """Class for webcomics"""

    @staticmethod
    @abc.abstractmethod
    def latest_id():
        """Return the uid of the latest comic in the collection"""

    @abc.abstractmethod
    def __init__(self, collection, number):
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


class XKCDComic(WebComic):
    """WebComic specialization for xkcd"""


class SinfestComic(WebComic):
    """Webcomic specialization for Sinfest"""
