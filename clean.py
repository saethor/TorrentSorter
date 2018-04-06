#! /usr/bin/env python

import sys
import getopt
import os
from pathlib import Path
import re
import shutil
import unicodedata


def nothing():
    two = 1 + 1
    # Function that extracts the name of the TV show from the folder name


def getName(directory):
    name = re.search(
        r'([\w\d \-\)\(\.\']*)((?= \d\d?. sería))|([\w\d \-\)\(\.\']*)((?= *season))|([\w\d \-\)\(\.\']*)((?= *sería))|([\w\d \-\)\(\.\']*)((?=\.\d\d\d\.))|([\w\d \-\)\(\.\']*)((?= *S\d))', directory, re.IGNORECASE)
    if name is not None:
        return name.group()
    else:
        return name


# Function that extracts the number of the TV show from the folder name
def getNumber(directory):
    number = re.search(
        r'S\d\d?|(?<=season\s)\d\d?|(?<=sería\s)\d\d?', directory, re.IGNORECASE)
    if number is not None:
        return number.group()
    else:
        return number


def main(argv):
    if len(sys.argv) < 3:
        raise ValueError(
            'Invalid argument count\nRun clean.py <source_folder> <destination_folder>')
    else:
        source = sys.argv[1]
        dest = sys.argv[2]
        if not os.path.isdir(source) or not os.path.isdir(dest):
            raise ValueError(
                'Invalid arguments\nRun clean.py <source_folder> <destination_folder>')

    TORRENT_DAY_DOT_COM = 'www.TorrentDay.com'
    # CWD
    cwd = os.getcwd()
    # source path as string and Pathlib object
    source_path = os.path.join(cwd, source)
    # destination path as string and Pathlib object
    dest_path = os.path.join(cwd, dest)

    # Create TEMP Folder for destination content
    Path(os.path.join(Path(source_path), 'TEMP_FOLDER')).mkdir(exist_ok=True)
    temp = os.path.join(source, 'TEMP_FOLDER')

    for path, dirs, files in os.walk(source):
        for directory in dirs:
            # IN FIRST ITERATION:
            # ONLY CHECK FOR WHOLE SEASONS AND MOVE TO DESIRED LOCATION
            # normalize utf-8 to NFC if needed
            directory = unicodedata.normalize('NFC', directory)
            if re.search(r'(sería|season|series) *\d\d?(?! *\d?\-)|(?<!\d)\d\d?\. *(season|sería|series)|(S\d\d?(?!\w))', directory, re.IGNORECASE):
                if re.search(r'(?<![ \d\w.])(\d\d?\. *(season|sería|series))|(?<![ \d\w.])(season|sería|series) *\d\d?|(?<![ \d\w.])S\d\d?(?![-])', directory, re.IGNORECASE):
                    # if current directory contains name of show, create folder and move
                    # if current directory is the source directory, do something later

                    curr_folder_name = str(Path(os.path.join(cwd, path)).name)
                    curr_path = os.path.join(cwd, path)
                    if curr_path != source_path:
                        # If the folder name starts with the torrent string then remove it and regex search the rest for the name
                        if TORRENT_DAY_DOT_COM in directory:
                            splitted = directory.split('-')
                            print('SPLITTED')
                            print(splitted[1])
                    print(directory)
                else:
                    print('move\n' + getName(directory) + '\nto new location\n')
                    nothing()
                    # if re.search(r'((series)|(sería)|(season))\s*\d\d?\s*\-\s*\d\d?|S\d{2}e\d\d?\s*\-\s*\d\d?', directory, re.IGNORECASE | re.UNICODE):
                    # print('Folder is a sequence of seasons')
                    # print(directory)
                    # print('----------------------------------------')

                    # IN SECOND ITERATION:
                    # PICK UP ALL REMAINING EPISODE FOLDERS
                    # If the folder is an episode of a show

                    # if re.search(r'S\d{2}E\d{2}', directory, re.IGNORECASE | re.UNICODE):
                    # print('Folder is a single episode')
                    # print(directory)
                    # print('----------------------------------------')
                    # TODO// IN SECOND ITERATION PICK UP ALL REMAINING EPISODE FILES



                    # execute main function
main(sys.argv)
