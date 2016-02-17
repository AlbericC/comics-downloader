#! /usr/bin/env python3.5
"""
This modules downloads all the comics from:
    - sinfest
    - xkcd
    - commitstrip (TODO)
In case the comics already exist on disk, skips the download, allowing to update a collection
"""

import begin

from path import Path
from tqdm import tqdm

DEFAULT_PATH = "~/Images/comics"


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


@begin.start(auto_convert=True)
def main(root_path: "The root folder for comics"=DEFAULT_PATH,
         xkcd: "Get the xkcd webcomics"=True,
         sinfest: "Get the sinfest webcomics"=True,
         commitstrip: "Get Commitstrips"=False):
    """
    Download comics from the internet onto disk.
    """

    collections = []
    if xkcd:
        collections.append('xkcd')
    if sinfest:
        collections.append('sinfest')
    if commitstrip:
        collections.append('commitstrip')
    # make those directoties if needed
    setup(root=root_path, subs=collections)
