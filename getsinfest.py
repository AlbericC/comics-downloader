#! /usr/bin/env python3.5
import imghdr
import os
import datetime
import zipfile
from concurrent.futures import ThreadPoolExecutor

import requests
import begin


# Useful functions
def make_cbz(dst_directory, src_directory):
    for year in range(2000, datetime.date.today().year + 1):
        with zipfile.ZipFile("Sinfest-{}.cbz".format(year), "w") as archive:
            for filename in os.listdir(src_directory):
                if filename.startswith(str(year)):
                    archive.write(src_directory + "/" + filename, arcname=filename)
        print("Sinfest-{}.cbz has been generated".format(year))


def file_needs_download(filename):
    """Checks whether a file exists, is corrupt, so has to be downloaded again
    also cleans garbage if detected"""
    if not os.path.isfile(filename):
        # many comics are *supposed* to be missing,
        # no need to output for these (uncomment for debug)
        # print("IS NOT FILE :", filename)
        return True
    elif os.path.getsize(filename) == 0:
        print("WRONG SIZE for", filename)
        return True
    elif filename.split(".")[-1] != "gif":
        print(filename, "IS NOT GIF")
        return True
    elif filename.split(".")[-1] in {"jpg", "gif", "png"} and imghdr.what(filename) is None:
        # Encoding error...
        print("WRONG FILE STRUCTURE for", filename)
        return True
    else:
        return False


def conditional_download(filename, base_url, caller=None):
    if file_needs_download(filename):
        src = requests.get(base_url + filename)
        # manage failure to download
        if src.status_code == 404:
            src.close()
            return  # ignore it, that file is simply missing.
        if src.status_code != 200:  # an error other than 404 occurred
            # print("Error {} on {}".format(src.status_code, filename))
            src.close()
            if caller:  # retry that file later
                caller.submit(conditional_download, filename, base_url, caller)
        # actually copy that file
        dst = open(filename, 'wb')
        dst.write(src.content)
        # gracefully close theses accesses.
        dst.close()
        src.close()
        print("\t{} : fetched.".format(filename))


def download_sinfest(target_folder):
    """
    Source function for the process
    Creates a directory and fetches Sinfest comics to populate it in full.
    """
    if not os.path.isdir(target_folder):
        os.makedirs(target_folder)
    os.chdir(target_folder)

    with ThreadPoolExecutor(max_workers=64) as executor:
        for file in ("".join([(datetime.date(2000, 1, 17) + datetime.timedelta(days=x)).isoformat(), ".gif"])
                     for x in range((datetime.date.today() - datetime.date(2000, 1, 17)).days + 1)):
            executor.submit(conditional_download, file, "http://www.sinfest.net/btphp/comics/", executor)


@begin.start
def run(path: "folder in which the comics must be downloaded" = os.path.expanduser("~/Sinfest/"),
        makecbz: "Compile CBZ comic book archives" = False):
    """Download the Sinfest WebComics"""
    download_sinfest(path)
    if makecbz:
        dst = path[:-1] if path.endswith('/') else path
        dst = "/".join(dst.split("/")[:-1])
        make_cbz(dst, path)
    print("Finished. Goodbye.")
    exit()
