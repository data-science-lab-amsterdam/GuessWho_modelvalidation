#
# - Check most recent date from target
# - Read from source everything after most recent date
# - Copy to target
#
from pathlib import Path
import os
import subprocess
import time


src_root = Path('/Volumes/data')
tgt_root = Path('./data')

images_path = Path('./images/faces_checked')
labels_path = Path('./labels_chacked')


def get_most_recent(directory, look_for='*.jpg'):
    files = directory.glob(look_for)
    return max(map(os.path.getctime, files))


def get_files_since(directory, timestamp, look_for='*.jpg'):
    files = directory.glob(look_for)
    return [f for f in files if os.path.getctime(f) > timestamp]


def copy_files(src_files, tgt_dir):
    if len(src_files) == 0:
        print("No new files, nothing to copy")
        return 0
    src_dir = str(src_files[0].parent)
    filenames_no_path = [x.name for x in src_files]
    cmd_parts = [
        'cp'
        src_dir + '/{' + ','.join(filenames_no_path) + '}',
        str(tgt_dir)
    ]
    print("Executing command: ")
    print(' '.join(cmd_parts))
    res = subprocess.call(cmd_parts)
    print('Result: {}'.format(res))
    return res


def update(src, tgt, look_for):
    most_recent_tgt = get_most_recent(dir=tgt,
                                      look_for=look_for
                                      )
    new_files = get_files_since(dir=src,
                                timestamp=most_recent_tgt,
                                look_for=look_for
                                )
    print("Files to copy:")
    print(new_files)

    return copy_files(new_files, tgt)


if __name__ == '__main__':
    while True:
        if not src_root.exists():
            print("Geen toegang tot {}".format(str(src_root)))
            print("Check de verbinding!")

        try:
            update(src_root/images_path, tgt_root/images_path, '*.jpg')
            update(src_root/labels_path, tgt_root/labels_path, '*.json')
        except Exception as e:
            print(e)
            print("Something went wrong. Will try again later")

        time.sleep(10)

