#! /usr/bin/env python3.5
from shutil import rmtree
import imghdr
import os
import queue
from threading import Thread
import datetime
import zipfile

import requests
import begin


# Useful functions
def make_cbz(dst_directory,src_directory):
    for year in range(2000, datetime.date.today().year + 1):
        with zipfile.ZipFile("Sinfest-{}.cbz".format(year), "w") as archive:
            for file in os.scandir(src_directory):
                if file.name.split("-")[0] == str(year):
                    archive.write(src_directory + "/" + file, arcname=file)
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
            return  # ignore it, that file is simply missing.
        if src.status_code != 200:  # an error other than 404 occurred
            print("Error {} on {}".format(src.status_code, filename))
            if caller:  # retry that file later
                caller.put((filename, caller))
        # actually copy that file
        dst = open(filename, 'wb')
        dst.write(src.content)
        # gracefully close theses accesses.
        dst.close()
        src.close()
        print("\t{} : fetched.".format(filename))


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
            t.daemon = True
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
    Source function for the process
    Creates a directory and fetches Sinfest comics to populate it in full.
    """
    if not os.path.isdir(target_folder):
        os.makedirs(target_folder)
    os.chdir(target_folder)

    f = lambda filename, caller: conditional_download(filename, "http://www.sinfest.net/btphp/comics/", caller)
    # Make a worker with this function and run it
    t = ThreadedWorker(function=f, number_of_threads=64)
    # structure of comprehended list is a bit complex to generate all file names
    files = [("".join([(datetime.date(2000, 1, 17) + datetime.timedelta(days=x)).isoformat(), ".gif"]), t)
             for x in range((datetime.date.today() - datetime.date(2000, 1, 17)).days + 1)]
    t.feed(files)
    t.join()


@begin.start
def run(path: "folder in which the comics must be downloaded" = os.path.expanduser("~/Sinfest/"),
        makecbz: "Compile CBZ comic book archives" = False,
        cleanup: "Remove the gifs after cbz generation (with makecbz)" = False):
    "Download the Sinfest WebComics"
    download_sinfest(path)
    if makecbz:
        make_cbz(os.path.pardir(path), path)
        if cleanup:
            rmtree(path)
    print("Finished. Goodbye.")
    exit()
