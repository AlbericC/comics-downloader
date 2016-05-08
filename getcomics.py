#! /usr/bin/env python3.5
"""
This modules downloads all the comics from:
    - sinfest
    - xkcd
    - CommitStrip
    - SMBC
In case the comics already exist on disk, skips the download, allowing to update a collection
"""

import sys

from concurrent.futures import ThreadPoolExecutor
from random import shuffle

import begin

from path import Path
from tqdm import tqdm

from comics import SinfestComic, XKCDComic, CommitStripComic, SMBCComic

AVAIL_COLLECTIONS = 'xkcd,sinfest,commitstrip,smbc'
COMICCLASSES = dict(zip(AVAIL_COLLECTIONS.split(','),
                        [XKCDComic, SinfestComic, CommitStripComic, SMBCComic]))

DEFAULT_PATH = Path("~/Images/comics")
WORKERS = 32


def setup(root, subs):
    """
    make the requested directories.
    If none, stop execution
    """
    root = Path(root).expand()
    if not subs:
        exit()
    for sub in subs:
        target = root / sub
        if not target.isdir():
            target.makedirs()


def progress(futures):
    """
    Display a progress bar while futures are done
    Works with a set of futures, or any stuff with a .done method
    """
    total = len(futures)
    with tqdm(total=total) as pbar:
        while futures:
            not_yet = []
            for fut in futures:
                if fut.done():
                    pbar.update(1)
                else:
                    not_yet.append(fut)
            futures = not_yet


def batch_submit(executor, func, items):
    """apply `func` to all `items` with executor, and return a collection of futures"""
    futures = []
    for item in items:
        fut = executor.submit(func, item)
        futures.append(fut)
    return futures


def process(comic):
    """proceed to the download of a single webcomic"""
    comic.download()


@begin.start(auto_convert=True)
def main(root_path: "The root folder for comics"=DEFAULT_PATH,
         commitstrip_lang: 'language in which to grab commitstrip {fr, en}'='fr',
         only: 'what comics to grab, separated with commas'=AVAIL_COLLECTIONS):
    """
    Download comics from the internet onto disk.
    """

    collections = only.split(',')
    comics_to_check = []

    dirs = [col for col in collections if col in COMICCLASSES]
    # make those directories if needed
    setup(root=root_path, subs=dirs)
    del dirs

    for collection in collections:
        if collection not in COMICCLASSES:
            print(collection + ": is not implemented, did you mistype?", file=sys.stderr)
            continue  # skip that

        class_ = COMICCLASSES[collection]
        # special case for commitstrip language
        if class_ is CommitStripComic:
            class_.LANG = commitstrip_lang
        class_.set_destination(root_path.joinpath(collection))
        comics_to_check += class_.all()

    # shuffle the list to make time more predictable during download
    shuffle(comics_to_check)

    executor = ThreadPoolExecutor(max_workers=WORKERS)
    futures = batch_submit(executor, func=process, items=comics_to_check)
    progress(futures)
