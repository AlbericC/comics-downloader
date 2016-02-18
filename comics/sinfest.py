"""
Defines a class for sinfest webcomics
"""

from datetime import date, timedelta

from .webcomic import WebComic


class SinfestComic(WebComic):
    """
    Class to describe Sinfest Comics

    Examples:
        >>> sinfests = SinfestComic.all()
        >>> SinfestComic.set_destination('~/sinfest/')
        >>> for comic in sinfests:
                comic.download()

    """

    BASE_URL = "http://www.sinfest.net/btphp/comics/"
    EXTENSION = '.gif'
    destination_folder = None

    @staticmethod
    def latest_id():
        """Return the uid of the latest comic in the collection"""
        today = date.today()
        return today.isoformat()

    @staticmethod
    def first_id():
        """return the uid of the first comic in this collection"""
        return date(2000, 1, 17).isoformat()

    @classmethod
    def all(cls):
        """prepare and return a list of all the currently existing comics"""
        out = []
        day = date(2000, 1, 17)
        num = 1
        today = date.today()
        while day <= today:
            out.append(SinfestComic(num))
            day += timedelta(days=1)
            num += 1
        return out

    def __init__(self, number):
        """Make a WebComic object"""
        super().__init__(number)
        firstdate = self.first_id()
        this_date = date(*[int(n) for n in firstdate.split('-')]) +\
            timedelta(days=number - 1)
        self.uid = this_date.isoformat()

    def __str__(self):
        return "Sinfest webcomic: {}".format(self.uid)

    def __repr__(self):
        return str(self)

    @property
    def alt_text(self):
        """There is no alternative text for Sinfest"""
        return None

    @property
    def image_url(self):
        """url of hosted image"""
        return self.BASE_URL + self.uid + self.EXTENSION

    @property
    def title(self):
        """title of the comic"""
        return 'sinfest {}'.format(self.number)

    @property
    def filename(self):
        return self.utitle + self.EXTENSION

    @property
    def utitle(self):
        """title of this comic, with number. Suitable to sort, and for file name"""
        return '{:>04}-{}'.format(self.number, self.uid).replace(' ', '_')
