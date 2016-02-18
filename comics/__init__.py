"""
Proposes tools to get infos, or download several webcomics
Not endorsed by the authors of the comics in any way.
"""

from .webcomic import WebComic
from .xkcd import XKCDComic
from .sinfest import SinfestComic
from .commitstrip import CommitStripComic

__all__ = ['WebComic', 'XKCDComic', 'SinfestComic', 'CommitStripComic']
__author__ = "Atrament"
