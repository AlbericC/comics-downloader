#! /usr/bin/env python3.5

from concurrent.futures import ThreadPoolExecutor
from path import Path

import begin
import xkcd

from tqdm import tqdm


DEFAULT_PATH = str(Path("~").expand() / "xkcd")


def fetch(number, destination, tries=3):
    """
    fetches a missing XKCD comic

    Args:
        number: the number id of the comic
        destination (path.Path): where to store the downloaded content.
    Returns:
        None
    """
    comic = xkcd.Comic(number)
    image_name = comic.imageName

    target = "{}/{:>04}-{}".format(destination, number, image_name)
    if Path(target).isfile() and Path(target + ".txt").isfile():
        return
    comic.download(outputFile=target)
    alt = comic.getAltText()
    # print("{:>5}: downloaded".format(number))
    with open(target + ".txt", "w") as spam:
        spam.write(alt)
        # print("{:>5}: alt text written".format(number))
    return 'Got {}'.format(number)


def setup(path):
    """Givent a path, setup the directory structure"""
    path = Path(path).expand()
    if not path.isdir():
        path.mkdir()
    return


def batch_submit(executor, items):
    """submit items to an executor, return a list of futures"""
    futures = []
    for comic_num, path in items:
        f = executor.submit(fetch, comic_num, path)
        futures.append(f)
    return futures


def progress(futures, total):
    """display a progress bar while futures are done"""
    with tqdm(total=total) as pbar:
        while futures:
            not_yet = []
            for fut in futures:
                if fut.done():
                    pbar.update(1)
                else:
                    not_yet.append(fut)
            futures = not_yet
    return


@begin.start
def run(path: "Path to which the comics are to be downloaded"=DEFAULT_PATH):
    """Get the full XKCD comics from the web"""
    setup(path)
    executor = ThreadPoolExecutor(max_workers=32)
    comics = xkcd.getLatestComicNum()
    items = [(num, path) for num in range(1, xkcd.getLatestComicNum() + 1)]
    futures = batch_submit(executor, items)
    progress(futures, total=comics)
