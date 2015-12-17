#! /usr/bin/env python3.5
from concurrent.futures import ThreadPoolExecutor
import begin
from path import Path
import xkcd


def fetch(number, destination: Path):
    """fetches a missing XKCD comic

    Args:
        number: the number id of the comic
        destination (path.Path): where to store the downloaded content.
    Returns:
        None
    """
    comic = xkcd.Comic(number)
    image_name = comic.imageName
    # print("trying {}".format(number))
    target = "{}/{:>04}-{}".format(destination, number, image_name)
    if Path(target).isfile() and Path(target + ".txt").isfile():
        # print("{:> 5}: ignored".format(number))
        return
    comic.download(outputFile=target)
    alt = comic.getAltText()
    print("{:>5}: downloaded".format(number))
    with open(target + ".txt", "w") as spam:
        spam.write(alt)
        # print("{:>5}: alt text written".format(number))


@begin.start
def run(path: "Path to which the comics are to be downloaded"
        = str(Path("~").expand() / "xkcd")):
    """Get the full XKCD comics from the web"""
    path = Path(path).expand()
    if not path.isdir():
        path.mkdir()
    with ThreadPoolExecutor(max_workers=32) as executor:
        for comic_num in range(1, xkcd.getLatestComicNum() + 1):
            executor.submit(fetch, comic_num, path)
            # print("submitted {:> 5}".format(comic_num))
