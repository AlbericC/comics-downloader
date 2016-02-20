"""Defines a class for SMBC Comics"""

# for whatever reasons, it might be necessary to actually crawl the website to get all the comics
# image location and naming is not consistent across comics
#
# first go to http://smbc-comics.com/index.php?id=1
# link for latest has id of latest comic in it
# it's in a a/href link with class 'last'
#
# each comic page is at http://smbc-comics.com/index.php?id=<comic-id>
# comic image for each page is in a <img> tag with id "comic"
#
# no title
# date is alt text of the comic picture, will serve as title
# 2 pictures
#
# the second (possible) picture is not present everytime.
# when present its the src of a <img> tag inside a <div> with id 'aftercomic'
# by chance, it happens to be the only img sith src beginning with http
#
# this script uses regexes instead of a html parser, as we are looking for few, punctual data.

import re
import html

import requests

from .webcomic import WebComic


class SMBCComic(WebComic):
    """Class for SMBC webcomics"""

    destination_folder = None
    latest = None
    IMG_TAG_REG = re.compile('<img.*?id="comic".*?>')
    BASE_URL = 'http://smbc-comics.com/'

    def __init__(self, number):
        """Make a SMBC WebComic object"""
        super().__init__(number)
        self.data = {}

    @classmethod
    def latest_id(cls):
        """Return the uid of the latest comic in the collection"""
        if cls.latest is not None:
            return cls.latest
        latest_regex = r'<a href=".*?\?id=(\d+)" class="last"'
        firstpage = requests.get('http://smbc-comics.com/index.php?id=1', timeout=10)
        matching = re.search(latest_regex, firstpage.text).groups()[0]
        cls.latest = int(matching)
        return cls.latest

    @staticmethod
    def first_id():
        """Return the uid of the first comic in the collection"""
        return 1

    @classmethod
    def all(cls):
        """ return an iterable of all the currently
        available comics form this collection """
        return [cls(num) for num in range(cls.first_id(), cls.latest_id() + 1)]

    def __str__(self):
        return "SMBC Webcomic {}".format(self.number)

    def __repr__(self):
        return str(self)

    def ensure_data(self):
        """Make sure data is collected from the net"""
        if self.data:
            return self.data
        comicpage = requests.get('http://smbc-comics.com/index.php?id={}'.format(self.number))
        imagetag = re.findall(self.IMG_TAG_REG, comicpage.text)[0]
        self.data['date'] = html.unescape(re.findall('title="(.*?)"', imagetag)[0])
        self.data['imgurl'] = self.BASE_URL + re.findall('src="(.*?)"', imagetag)[0]
        # second image if any ?
        button_img = re.findall("<img src='(http.*?)'.*?>", comicpage.text)  # no good, but meh
        #  The sole <img> tag with src fully qualified is the button picture... bad way to do it.
        if button_img:  # found one (or more)
            self.data['imgurl2'] = button_img[0]
        return self.data

    @property
    def alt_text(self):
        """No Alt text for this comics collection"""
        return None

    @property
    def image_url(self):
        """url of hosted image"""
        if not self.ensure_data():
            return
        return self.data['imgurl']

    @property
    def title(self):
        """title of this comic"""
        if not self.ensure_data():
            return 'no-title'
        return self.data['date']

    @property
    def utitle(self):
        """title of this comic, with number. Suitable to sort"""
        return '{:>04}-{}'.format(self.number, self.title)

    @property
    def filename(self):
        """The candidate filename for this comics image"""
        if not self.ensure_data():
            return
        return self.utitle + '_a.' + self.data['imgurl'].split('.')[-1]

    def download(self):
        out = [super().download()]
        # also get te second image (if any)
        if out[0] is None:
            return
        if 'imgurl2' in self.data:
            src = requests.get(self.data['imgurl2'], timeout=10)
            if src.status_code != 200:
                return
            targetfilename = self.utitle + '_b.' + self.data['imgurl2'].split('.')[-1]
            target = self.destination_folder.joinpath(targetfilename)
            with open(target, 'wb') as dest:
                dest.write(src.content)
            out.append(target)
        return out
