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
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

## REGEX CONSTANTS ##

# parse string and stop when keywords season/series/sería are reached
get_name_cut_on_season_re = r'(.*)((?= *season|series|sería))|(.*)((?=.S\d\d?))|(.*)((?= *S\d\dE\d\d))'
# parse string and stop when pattern S01E02 are reached
get_name_cut_on_episode_re = r'(.*)((?= *S\d\dE\d\d))'

# regex for the number of the season
get_season_number = r'S\d\d?|(?<=season) *\d\d?|S\d\d?|(?<=sería) *\d\d?|S\d\d?|(?<=series) *\d\d?|(?<!\d)\d\d?(?=\. *season)|(?<!\d)\d\d?(?=\. *sería)|(?<!\d)\d\d?(?=\. *series)'

# regex for finding a season
get_season_re = r'(sería|season|series) *\d\d?(?! *\d?\-)|(?<!\d)\d\d?\. *(season|sería|series)|(S\d\d?(?!\w))'
# helper sub-regex to determine if the name of a season folder does not contain the name of the show, then the current directory needs to be reviewed
check_show_name_missing = r'(?<![ \d\w.])(\d\d?\. *(season|sería|series))|(?<![ \d\w.])(season|sería|series) *\d\d?|(?<![ \d\w.])S\d\d?(?![-])'

# regex for finding single episode as folder or file
get_single_episode_re = r'S\d\d?E\d\d'

# regex to find a folder containing a sequence of seasons
get_season_sequence = r'(series|season|sería|S\d\d?E) *\d\d? *\- *\d\d? *'


# Specific regexes for some edge cases

uk_re = r'(.*)((?= \(Uk))'
year_re = r'(19|20)\d{2}'

DEBUG = True
NOT_A_SHOW = 'NOT_A_SHOW'

# Function that extracts the name of the TV show from the folder name

# Common leftovers that needs to be removed from names
IRL = 'Irl'
CA = 'Ca'
THE_COMPLETE = 'The Complete'
COMPLETE = 'complete'
UK = '(Uk)'

# if name contains The complete
# if name contains (
# If name ends with SXX


# Helper function that is ment for some edge cases
# ideally this is the only function that needs to be improved over time
def cleanName(name):
    # Remove seasons that end with Irl
    if name.strip().endswith(IRL):
        name = name.strip()[:-len(IRL)]
    # Remove seasons that end with Ca
    if name.strip().endswith(CA):
        name = name.strip()[:-len(CA)]
    # Remove season that are followed by (Uk)
    if UK in name:
        clean_name = re.search(uk_re, name, re.IGNORECASE)
        if clean_name is not None:
            name = clean_name.group()
    clean_name = re.search(year_re, name)
    # Remove all years that are in season names
    if clean_name is not None:
        year = clean_name.group()
        name = name.replace(year, '')
    # Remove trailing season/episode pattern if they were along with the season name
    clean_name = re.search(get_name_cut_on_season_re, name, re.IGNORECASE)
    if clean_name is not None:
        name = clean_name.group()
    # Remove The Complete or Complete
    if THE_COMPLETE in name:
        name = name.split(THE_COMPLETE)[0]
    if COMPLETE in name:
        name = name.split(COMPLETE)[0]
    return name


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
        show_name = cleanName(show_name)
        return show_name.strip()
    else:
        return directory


# Function that extracts the number of the TV show from the folder name
def getNumber(directory):
    number = re.search(get_season_number, directory, re.IGNORECASE)
    if number is not None:
        season = number.group().strip()
        season = season.replace('S', '')
        season = season.replace('s', '')
        season = season.zfill(2)
        return f'Season {season}'
    else:
        return 'NOT_A_SHOW'


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)


def main(source, dest):
    shows = set()
    success = []
    failed = []
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

    tv_shows = defaultdict(set)

    for path, dirs, files in os.walk(source):
        # Testing stuff
        
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
                    season = getNumber(directory)

                    show_path = os.path.join(dest_path, curr_folder_name)
                    season_path = os.path.join(show_path, season)
                    os.makedirs(show_path, exist_ok=True)
                    os.makedirs(season_path, exist_ok=True)

                    logger.debug(f'TV show: {curr_folder_name} needs to be moved to correct')
                else:
                    name = getName(directory, get_name_cut_on_season_re)
                    season = getNumber(directory)
                    if name is not None and name is not '':
                        logging.debug(f'TV show: {name} needs to be moved to folder')

                        show_path = os.path.join(dest_path, name)
                        season_path = os.path.join(show_path, season)
                        os.makedirs(show_path, exist_ok=True)
                        os.makedirs(season_path, exist_ok=True)
                    else:
                        pass
            if re.search(get_single_episode_re, directory, re.IGNORECASE | re.UNICODE):
                name = getName(directory, get_name_cut_on_episode_re)
                season = getNumber(directory)

                if name is not None and name is not '':
                    logger.debug(f'TV show: {name} needs to be moved to folder')
                    tv_shows[name].add(season)

                    show_path = os.path.join(dest_path, name)
                    season_path = os.path.join(show_path, season)
                    os.makedirs(show_path, exist_ok=True)
                    os.makedirs(season_path, exist_ok=True)
                else:
                    pass
            if re.search(get_season_sequence, directory, re.IGNORECASE | re.UNICODE):
                logger.debug(f'Folder: {directory} is a sequence of seasons')
        
        
        for fil in files:
            fil = unicodedata.normalize('NFC', fil)
            name = getName(fil, get_name_cut_on_episode_re)
            season = getNumber(fil)
            if name == NOT_A_SHOW or season == NOT_A_SHOW:
                continue
            file_src = os.path.join(path, fil)
            file_dest = os.path.join(dest_path, name, season)
            if not os.path.exists(file_dest):
                os.makedirs(os.path.join(dest_path, name), exist_ok=True)
                os.makedirs(os.path.join(dest_path, name, season), exist_ok=True)
            try:
                shutil.copy(file_src, file_dest)
                success.append(fil)
                logger.info(f'Copied file {file_src} to {file_dest}')                
            except FileNotFoundError:
                failed.append(fil)
                logger.error(f'Failed to copy file {file_src}')
        
    print('--------------------------------')
    print('REPORT')
    print(f'Successfully copied {len(success)}')
    print(f'Failed: {len(failed)}')
    print('--------------------------------')
        
                

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloaded Tv show Sorter")
    parser.add_argument('source', metavar='source', type=str,
                        help='Source of the folder containing all the tv shows')
    parser.add_argument('dest', metavar='destination', type=str,
                        help='Destination where sorted tv shows should end')
    args = parser.parse_args()

    main(args.source, args.dest)
