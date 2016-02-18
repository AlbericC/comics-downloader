"""Defines a class for commitstrip webcomics """

# for whatever reasons, it might be necessary to actually crawl the website to get all the comics
# other way round is to check by date, go to http://www.commitstrip.com/fr/YYYY/MM/DD/
# returns a 404 if there is no commitstrip that day, other there is an intermediate page
# in which regex `http://www.commitstrip.com/fr/YYYY/MM/DD/[^ "]+` is a url to the comic page.
# In this comic page then,
# regex `http://www.commitstrip.com/wp-content/uploads/YYYY/MM/[^ "]+` matches for 2 strings,
# the second one is the link to the picture.
# There is no alt text.
# The title text is inside pages title
# regex = re.compile('<title>(.*) \|.*</title>')
# m = regex.search(r.text)
# m.groups()[0]  # gives the Comics title

import re
import html

from datetime import date, timedelta

import requests

from .webcomic import WebComic


class CommitStripComic(WebComic):
    """Class for Commit strip webcomics"""

    destination_folder = None
    FIRST = {'y': 2012, 'm': 2, 'd': 22}
    DATEPAGE_TEMPLATE = 'http://www.commitstrip.com/fr/{y:>04}/{m:>02}/{d:>02}/'
    COMICPAGE_TEMPLATE = 'http://www.commitstrip.com/wp-content/uploads/{y:>04}/{m:>02}/'
    TITLE_REGEX = re.compile(r'<title>(.*) \|.*</title>')
    LANG = 'en'

    def __init__(self, number):
        """Make a CommitStrip WebComic object"""
        super().__init__(number)
        self.data = ''

    @staticmethod
    def latest_id():
        """Return the uid of the latest comic in the collection"""
        today = date.today()
        return today.year, today.month, today.day

    @classmethod
    def first_id(cls):
        """Return the uid of the first comic in the collection"""
        return cls.FIRST['y'], cls.FIRST['m'], cls.FIRST['d'],

    @classmethod
    def all(cls):
        """ return an iterable of all the currently
        available comics form this collection
        """
        out = []
        num = 1
        day = date(cls.FIRST['y'], cls.FIRST['m'], cls.FIRST['d'])
        today = date.today()
        while day <= today:
            out.append(CommitStripComic(num))
            day += timedelta(days=1)
            num += 1
        return out

    def ensure_data(self):
        """download the data when and if necessary"""
        if self.data is not '':
            return self.data
        self.data = None
        this_date = date(self.FIRST['y'], self.FIRST['m'], self.FIRST['d'])
        this_date += timedelta(days=self.number)
        url = self.DATEPAGE_TEMPLATE.format(y=this_date.year, m=this_date.month, d=this_date.day)
        firstpage = requests.get(url, timeout=10)
        if firstpage.status_code == 404:
            return
        # crawl the second step: find the regex to the comicpage
        new_url = re.compile(url + '[^ "]+').findall(firstpage.text)[0]
        comicpage = requests.get(new_url)
        if comicpage.status_code != 200:
            return
        coregex = re.compile(self.COMICPAGE_TEMPLATE.format(y=this_date.year, m=this_date.month) +
                             '[^ "]+')
        links = coregex.findall(comicpage.text)
        # almost there...
        matchintitle = self.TITLE_REGEX.search(comicpage.text)
        title = html.unescape(matchintitle.groups()[0]).replace(' | CommitStrip', '')
        self.data = {'img-en': links[0], 'title': title, 'img-fr': links[1]}
        return self.data  # return a non-empty object to signal success

    def __str__(self):
        if self.ensure_data():
            return "CommitStrip Webcomic {}: {} ".format(self.number, self.title)
        else:
            return 'A missing CommitStrip for number {}'.format(self.number)

    def __repr__(self):
        return str(self)

    @property
    def alt_text(self):
        """None for Commit strips"""
        return None

    @property
    def image_url(self):
        """url of hosted image"""
        if not self.ensure_data():
            return
        return self.data['img-{}'.format(self.LANG)]

    @property
    def title(self):
        """title of this comic"""
        if not self.ensure_data():
            return
        return self.data['title']

    @property
    def utitle(self):
        """title of this comic, with number. Suitable to sort"""
        return '{:>04}-{}'.format(self.number, self.title)

    @property
    def filename(self):
        """The candidate filename for this comics image"""
        if not self.ensure_data:
            return
        imgname = self.image_url.split('/')[-1]
        return '{:>04}-{}'.format(self.number, imgname)
