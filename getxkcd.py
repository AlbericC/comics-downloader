#! /usr/bin/env python3.5
from concurrent.futures import ThreadPoolExecutor
import begin
from path import Path
import xkcd
from time import sleep


def fetch(number, destination):
    """fetches a missing XKCD comic

    Args:
        number: the number id of the comic
        destination (path.Path): where to store the downloaded content.
    Returns:
        None
    """
    retry = 3
    while retry:
        try:
            comic = xkcd.Comic(number)
            image_name = comic.imageName
        except HTTPError as e:
            if e.code != 404:
                print(e)
                retry -= 1
                sleep(0.5)
            else:
                return 'Missing: {}'.format(number)

    # print("trying {}".format(number))
    target = "{}/{:>04}-{}".format(destination, number, image_name)
    if Path(target).isfile() and Path(target + ".txt").isfile():
        # print("{:> 5}: ignored".format(number))
        return 'Nothing to do for {}'.format(number)
    comic.download(outputFile=target)
    alt = comic.getAltText()
    print("{:>5}: downloaded".format(number))
    with open(target + ".txt", "w") as spam:
        spam.write(alt)
        # print("{:>5}: alt text written".format(number))
    return 'Got {}'.format(number)


@begin.start
def run(path: "Path to which the comics are to be downloaded"=
        str(Path("~").expand() / "xkcd")):
    """Get the full XKCD comics from the web"""
    path = Path(path).expand()
    if not path.isdir():
        path.mkdir()
    with ThreadPoolExecutor(max_workers=32) as executor:
        futures = []
        for comic_num in range(1, xkcd.getLatestComicNum() + 1):
            f = executor.submit(fetch, comic_num, path)
            futures.append(f)
            print('future submitted')
        for f in futures:
            print('checking a future {}'.format(f.result(timeout=10)))
