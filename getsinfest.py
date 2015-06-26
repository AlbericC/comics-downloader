#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------
# Author:      Atrament
# Licence:     CC-BY-SA https://creativecommons.org/licenses/by-sa/4.0/
# ---------------------------------------------------------------------
# All libs are part of standard distribution for python 3.4

import imghdr
import os
import queue
from threading import Thread
import datetime
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
import zipfile
import sys


# Useful functions
def make_cbz(directory):
    for year in range(2000, datetime.date.today().year + 1):
        with zipfile.ZipFile("Sinfest-{}.cbz".format(year), "w") as archive:
            for gif_file in [x for x in os.listdir(directory) if x.split("-")[0] == str(year)]:
                archive.write(directory + '/' + gif_file, arcname=gif_file)
        print("Sinfest-{}.cbz has been generated".format(year))


def confirm(prompt):
    if input("{} (y/n)".format(prompt)) in "yY":
        return True
    else:
        return False


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
        try:
            src = urlopen(base_url + filename)
            dst = open(filename, 'wb')
            dst.write(src.read())
            # gracefully close theses accesses.
            dst.close()
            src.close()
            print("\t{} : fetched.".format(filename))
        except HTTPError:
            # many days do not have a comic published.
            # no need to flood the console for this.
            pass
        except URLError:
            print("network error on {}".format(filename))
        except TimeoutError:
            print("Timout on {}".format(filename))
        except ConnectionResetError:
            if caller:
                caller.put((filename,caller))  # try this url again later.
        finally:
            # clean garbage on disk, useful if failure occurred.
            file_needs_download(filename)


class ThreadedWorker():
    def __init__(self, function=None, number_of_threads=8):
        self.queue = queue.Queue()

        def func():
            while True:
                item = self.queue.get()
                if function:
                    function(*item)
                else:
                    print(item, "is being processed.")
                self.queue.task_done()

        self.function = func

        for i in range(number_of_threads):
            t = Thread(target=self.function, name="Thread-{:03}".format(i))
            # t.daemon = True
            t.start()

    def put(self, object_to_queue):
        self.queue.put(object_to_queue)

    def join(self):
        self.queue.join()

    def feed(self, iterator):
        for task in iterator:
            self.queue.put(task)


def download_sinfest(target_folder):
    """
    Creates a directory and fetches Sinfest comics to populate it in full.
    """
    if not os.path.isdir(target_folder):
        os.makedirs(target_folder)
    os.chdir(target_folder)

    f = lambda filename, caller: conditional_download(filename, "http://www.sinfest.net/btphp/comics/", caller)
    # Make a worker with this function and run it
    t = ThreadedWorker(function=f, number_of_threads=32)
    # structure of comprehended list is a bit complex to generate all file names
    files = [("".join([(datetime.date(2000, 1, 17)+datetime.timedelta(days=x)).isoformat(), ".gif"]), t)
             for x in range((datetime.date.today() - datetime.date(2000, 1, 17)).days + 1)]
    t.feed(files)
    t.join()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[-1] in "y Y -y -Y yes YES -yes -YES".split():
        folder = os.path.expanduser("~/Pictures/Sinfest/").replace("\\", "/")
        print("\nproceeding to download...")
        download_sinfest(folder)
        print("\ngenerating comic book files (.cbz)...")
        os.chdir(folder)
        os.chdir("..")
        make_cbz(folder)
        exit()
    else:
        folder = os.path.expanduser("~/Pictures/Sinfest/").replace("\\", "/")
        while not confirm("Target to downloads is {} ?".format(folder)):
            folder = input("Please enter new folder (N to abort) :")
            if folder in "nN":
                exit(0)
        if confirm("Proceed to download ?"):
            download_sinfest(folder)
        if confirm("Do you want to generate cbz (comic books) files ?"):
            os.chdir("..")
            make_cbz(folder)
        if confirm("Do you wish to erase the gif files (to keep only cbz ?"):
            from shutil import rmtree
            if confirm("Are you really really sure ?"):
                num = len(os.listdir(folder))
                if confirm("Not to worry you, but {} files are about to be deleted.".format(num)):
                    rmtree(folder)
                    print("It's done. You told me to do it. I did it. No complaining now.")
        input("Finished. Please press Enter")
