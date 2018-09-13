#
# - Check most recent date from target
# - Read from source everything after most recent date
# - Copy to target
#
from pathlib import Path
import os
import subprocess
import time
import logging


logging.basicConfig(level=logging.INFO)


src_root = Path('/Volumes/data')
tgt_root = Path('./data')

images_path = Path('./images/faces_checked')
labels_path = Path('./labels_checked')


def get_most_recent(directory, look_for='*.jpg'):
    files = directory.glob(look_for)
    try:
        return max(map(os.path.getctime, files))
    except:
        return 0


def get_files_since(directory, timestamp, look_for='*.jpg'):
    files = directory.glob(look_for)
    return [f for f in files if os.path.getctime(f) > timestamp]


def copy_files(src_files, tgt_dir):
    if len(src_files) == 0:
        logging.info("No new files, nothing to copy")
        return 0

    for file in src_files:
        logging.info(str(file))
        res = subprocess.call(['cp', str(file), tgt_dir])
        if res != 0:
            logging.error('Something went wrong while copying!')


def update(src, tgt, look_for):
    most_recent_tgt = get_most_recent(directory=tgt,
                                      look_for=look_for
                                      )
    new_files = get_files_since(directory=src,
                                timestamp=most_recent_tgt,
                                look_for=look_for
                                )

    return copy_files(new_files, tgt)


if __name__ == '__main__':
    while True:
        if not src_root.exists():
            logging.info("Geen toegang tot {}".format(str(src_root)))
            logging.info("Check de verbinding!")

        try:
            update(src_root/images_path, tgt_root/images_path, '*.jpg')
            update(src_root/labels_path, tgt_root/labels_path, '*.json')
        except Exception as e:
            logging.info(e)
            logging.info("Something went wrong. Will try again later")

        time.sleep(5)

