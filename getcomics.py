#! /usr/bin/env python3.5
"""
This modules downloads all the comics from:
    - sinfest
    - xkcd
In case the comics already exist on disk, skips the download, allowing to update a collection
"""

from concurrent.futures import ThreadPoolExecutor

import begin

from path import Path
from tqdm import tqdm

from comics import SinfestComic, XKCDComic

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
         xkcd: "Get the xkcd webcomics"=True,
         sinfest: "Get the sinfest webcomics"=True,
         commitstrip: "Get Commitstrips"=False):
    """
    Download comics from the internet onto disk.
    """

    collections = []
    comics_to_check = []
    if xkcd:
        collections.append('xkcd')
        XKCDComic.set_destination(root_path.joinpath('xkcd'))
        comics_to_check += XKCDComic.all()
    if sinfest:
        collections.append('sinfest')
        SinfestComic.set_destination(root_path.joinpath('sinfest'))
        comics_to_check += SinfestComic.all()
    if commitstrip:
        collections.append('commitstrip')
    # make those directories if needed
    setup(root=root_path, subs=collections)

    executor = ThreadPoolExecutor(max_workers=WORKERS)
    futures = batch_submit(executor, func=process, items=comics_to_check)
    progress(futures)
