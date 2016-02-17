#! /usr/bin/env python3.5
"""
This modules downloads all the comics from:
    - sinfest
    - xkcd
    - commitstrip (TODO)
In case the comics already exist on disk, skips the download, allowing to update a collection
"""

import datetime

from concurrent.futures import ThreadPoolExecutor
from collections import namedtuple

import begin
import xkcd

from path import Path
from tqdm import tqdm

DEFAULT_PATH = "~/Images/comics"
WORKERS = 16

Comic = namedtuple("Comic", ("comic_name", "uid", 'task', 'root_path'))

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


def get_comics_list(comic, root_path, task):
    """Given a comics name, return a list of `Comic` objects"""
    if comic is 'sinfest':
        this_one = datetime.date(2000, 1, 17)
        comics = []
        while this_one < datetime.date.today():
            uid = this_one.isoformat()
            comics.append(Comic(comic_name=comic, uid=uid, task=task, root_path=root_path))
            this_one += datetime.timedelta(days=1)
        return comics
    if comic is 'xkcd':
        latest = xkcd.getLatestComicNum()
        return [Comic(comic_name=comic, uid=num, task=task, root_path=root_path)
                for num in range(1, latest + 1)]
    assert False is comic  # TODO


def exists(comic):
    """True if the file for this comic does exist"""


def fetch(comic):
    """manages fetching the comic"""
    # verify wether already exists
    # if missing, get it


def batch_submit(executor, tasks):
    """Submit all tasks to the executor, returns the futures"""
    futures = []
    for task in tasks:
        fut = executor.submit(task.task, task)
        futures.append(fut)
    return futures


def progress(futures):
    """display a progress bar while futures are done"""
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
         xkcd_get: "Get the xkcd webcomics"=True,
         sinfest_get: "Get the sinfest webcomics"=True,
         commitstrip_get: "Get Commitstrips"=False):
    """
    Download comics from the internet onto disk.
    """

    # prepare a list of subdirs to consider
    labs = [label
            for label, demanded in
            {"xkcd": xkcd_get, "sinfest": sinfest_get, "commitstrip": commitstrip_get}
            if demanded]
    # make those
    setup(root=root_path, subs=labs)
    # create an executor
    executor = ThreadPoolExecutor(max_workers=WORKERS)
    futures = []
    for label in labs:
        # submit label to executor to get all comics ids
        comics = get_comics_list(label, root_path, task=fetch)
        futures += batch_submit(executor, comics)
    progress(futures)
