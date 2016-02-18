"""Defines a class for SMBC Comics"""

# for whatever reasons, it might be necessary to actually crawl the website to get all the comics

from .webcomic import WebComic


class SMBCComic(WebComic):
    """Class for SMBC webcomics"""
    # TODO: implement

    destination_folder = None

    def __init__(self, number):
        """Make a WebComic object"""
        super().__init__(number)

    @staticmethod
    def latest_id():
        """Return the uid of the latest comic in the collection"""

    @staticmethod
    def first_id():
        """Return the uid of the first comic in the collection"""

    @classmethod
    def all(cls):
        """
        return an iterable of all the currently
        available comics form this collection
        """

    def __str__(self):
        return "Webcomic"

    def __repr__(self):
        return "Webcomic"

    @property
    def alt_text(self):
        """The alt text for this comic, or an empty string"""
        return 'Alternative text'

    @property
    def image_url(self):
        """url of hosted image"""
        return 'http://www.example.com/'

    @property
    def title(self):
        """title of this comic"""
        return "Placeholder title"

    @property
    def utitle(self):
        """title of this comic, with number. Suitable to sort"""
        return '{:>04}-{}'.format(self.number, self.title)

    @property
    def filename(self):
        """The candidate filename for this comics image"""
