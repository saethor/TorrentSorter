#! /usr/bin/env python

import sys
import getopt
import os
from pathlib import Path
import re
import shutil
import unicodedata
import argparse
from collections import defaultdict


## REGEX CONSTANTS ##

# parse string and stop when keywords season/series/sería are reached
get_name_cut_on_season_re = r'(.*)((?= *season|series|sería))'
# parse string and stop when pattern S01E02 are reached
get_name_cut_on_episode_re = r'(.*)((?= *S\d\dE\d\d))'

# regex for the number of the season
get_season_number = r'S\d\d?|(?<=season|sería|series\s)\d\d?'

# regex for finding a season
get_season_re = r'(sería|season|series) *\d\d?(?! *\d?\-)|(?<!\d)\d\d?\. *(season|sería|series)|(S\d\d?(?!\w))'
# helper sub-regex to determine if the name of a season folder does not contain the name of the show, then the current directory needs to be reviewed
check_show_name_missing = r'(?<![ \d\w.])(\d\d?\. *(season|sería|series))|(?<![ \d\w.])(season|sería|series) *\d\d?|(?<![ \d\w.])S\d\d?(?![-])'

# regex for finding single episode as folder or file
get_single_episode_re = r'S\d\d?E\d\d'

# regex to find a folder containing a sequence of seasons
get_season_sequence = r'(series|season|sería|S\d\d?E) *\d\d? *\- *\d\d? *'


# Function that extracts the name of the TV show from the folder name
def getName(directory, regex):
    name = re.search(regex, directory, re.IGNORECASE)
    if name is not None:
        name = name.group()
        show_name = name.split('.')

        if len(show_name) == 1:
            show_name = name.split('-')

        show_name = ' '.join(show_name)

        # Remove punctuation
        show_name = ''.join(show_name.split("'")).title()

        return show_name.strip()
    else:
        return name


# Function that extracts the number of the TV show from the folder name
def getNumber(directory):
    number = re.search(get_season_number, directory, re.IGNORECASE)
    if number is not None:
        return number.group()
    else:
        return number

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def main(source, dest):
    # Check if source folder exists
    if not os.path.isdir(source):
        raise ValueError(
            'Invalid arguments\nRun clean.py <source_folder> <destination_folder>')

    if not os.path.isdir(dest):
        os.makedirs(dest)

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

     tv_shows = set()

    for path, dirs, files in os.walk(source):
        # Testing stuff
        for f in files:
            name = getName(f, get_name_cut_on_episode_re)
            if name == None:
                continue
            tv_shows.add(name)
            continue
        # End of testing stuff

        for directory in dirs:
            # IN FIRST ITERATION:
            # ONLY CHECK FOR WHOLE SEASONS AND MOVE TO DESIRED LOCATION
            # normalize utf-8 to NFC if needed
            directory = unicodedata.normalize('NFC', directory)
            if TORRENT_DAY_DOT_COM in directory:
                directory = directory.split('-')[1]
            if re.search(get_season_re, directory, re.IGNORECASE):
                if re.search(check_show_name_missing, directory, re.IGNORECASE):

                    # if current directory contains name of show, create folder and move
                    # if current directory is the source directory, do something later
                    curr_folder_name = str(Path(os.path.join(cwd, path)).name)
                    curr_path = os.path.join(cwd, path)

                    print('TV show: ' + curr_folder_name +
                          ' needs to be moved to correct')
                else:
                    name = getName(directory, get_name_cut_on_season_re)
                    if name is not None and name is not '':
                        print('TV show: ' + name +
                              ' needs to be moved to folder')
                    else:
                        pass
            if re.search(get_single_episode_re, directory, re.IGNORECASE | re.UNICODE):
                name = getName(directory, get_name_cut_on_episode_re)
                if name is not None and name is not '':
                    print('TV show: ' + name +
                          ' needs to be moved to folder')
                else:
                    pass
            if re.search(get_season_sequence, directory, re.IGNORECASE | re.UNICODE):
                print('Folder: ' + directory + ' is a sequence of seasons')
    # Printing out what I found
    for show in tv_shows:
        # print(show)
        pass
    print(len(tv_shows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloaded Tv show Sorter")
    parser.add_argument('source', metavar='source', type=str,
                        help='Source of the folder containing all the tv shows')
    parser.add_argument('dest', metavar='destination', type=str,
                        help='Destination where sorted tv shows should end')
    args = parser.parse_args()

    main(args.source, args.dest)
