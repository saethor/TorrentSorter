#! /usr/bin/env python

import sys
import getopt
import os
from pathlib import Path
import re
import shutil
import unicodedata
import argparse
from collections import defaultdict, Counter
import logging
import platform

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

shows = set()
success = []
failed = []

## REGEX CONSTANTS ##

# extract season name from folder
get_name_cut_on_season_re = r'(.*)((?= *season|series|sería))|(.*)((?=.S\d\d?))|(.*)((?= *S\d\dE\d\d))'
# extract season name from folder
get_name_cut_on_episode_re = r'(.*)((?= *S\d\dE\d\d))'

# extract season name from single file
get_name_from_file_re = r'(.*)((?= *season|series|sería|S\d\d?|\.\d|\d\d?x\d\d?))'

# regex for the number of the season
get_season_number = r'S\d\d?|(?<=season) *\d\d?|S\d\d?|(?<=sería) *\d\d?|S\d\d?|(?<=series) *\d\d?|(?<!\d)\d\d?(?=\. *season)|(?<!\d)\d\d?(?=\. *sería)|(?<!\d)\d\d?(?=\. *series)|^\d\d?$'

# regex to get the season and number as it is from the file or folder name
get_original_season_and_number = r'(season|sería|series) *\d\d?|\d\d? *\. *(season|sería|series)'

# regex for finding a season
get_season_re = r'(sería|season|series) *\d\d?(?! *\d?\-)|(?<!\d)\d\d?\. *(season|sería|series)|(S\d\d?(?!\w))|^\d\d?$'
# helper sub-regex to determine if the name of a season folder does not contain the name of the show, then the current directory needs to be reviewed
check_show_name_missing = r'(?<![ \d\w.])(\d\d?\. *(season|sería|series))|(?<![ \d\w.])(season|sería|series) *\d\d?|(?<![ \d\w.])S\d\d?(?![-])|^\d\d?$'

# regex for finding an episode
get_episode_re = r'\d\d?x\d\d?|s\d\d?e\d\d?|\.\d\d\d?\.|(season|series|sería) *[\w\d] *(episode|þáttur) *[\d\w]'


# regex for finding single episode as folder or file
get_single_episode_re = r'S\d\d?E\d\d'

# regex to find a folder containing a sequence of seasons
get_season_sequence = r'(series|season|sería|S\d\d?E) *\d\d? *\- *\d\d? *'


# Specific regexes for some edge cases

uk_re = r'(.*)((?= \(Uk))'
year_re = r'(19|20)\d{2}'

DEBUG = False
NAME_OR_SEASON_NOT_FOUND = 'NAME_OR_SEASON_NOT_FOUND'

# Function that extracts the name of the TV show from the folder name

# Common leftovers that needs to be removed from names
IRL = 'Irl'
CA = 'Ca'
THE_COMPLETE = 'The Complete'
COMPLETE = 'complete'
UK = '(Uk)'
TORRENT_DAY = 'Torrentday'

extensions = ['avi', 'mp4', 'mov', 'mpg', 'mkv', 'm4v', 'wmv']


def moveToDest(fil, source, dest):
    ext = fil.split('.')[-1]
    if ext.lower() not in extensions:
        return

    if not os.path.isdir(source):
        try:
            shutil.copy(source, dest)
            success.append(fil)
            logger.info(f'Copied file {source} to {dest}')
        except FileNotFoundError:
            failed.append(fil)
            logger.warning(f'Failed to copy file {source}')
    else:
        # TODO:: Traverse each folder and copy the files found for cases like Shameless where
        #        each episode is inside a folder
        pass


# if name contains The complete
# if name contains (
# If name ends with SXX

# Helper function that is ment for some edge cases
# ideally this is the only function that needs to be improved over time
def cleanName(name):
    if TORRENT_DAY in name:
        name = name.split('-')[1]
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

    # Remove punctuation
    name = name.replace("'", "")

    # Replace . with space if any
    name = name.replace('.', ' ')

    # Remove extra hypens in name
    name = name.replace('-', ' ')
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
        return cleanName(directory)


def getOriginalSeasonAndNumber(directory):
    season = re.search(get_original_season_and_number,
                       directory, re.IGNORECASE)
    if season is not None:
        return season.group()
    else:
        return 'NAME_OR_SEASON_NOT_FOUND'


# Function that extracts the number of the TV show from the folder name
def getNumber(directory):
    number = re.search(get_season_number, directory, re.IGNORECASE)
    if number is not None:
        season = number.group().strip()
        season = season.replace('S', '')
        season = season.replace('s', '')
        season = season.zfill(2)
        return f'Season {season}'
    elif directory.isdigit():
        season = directory.zfill(2)
        return f'Season {season}'
    else:
        return 'NAME_OR_SEASON_NOT_FOUND'


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

    # CWD
    cwd = os.getcwd()
    print(platform.system())
    # source path as string and Pathlib object
    source_path = os.path.join(cwd, source)

    # destination path as string and Pathlib object
    dest_path = os.path.join(cwd, dest)

    tv_shows = defaultdict(set)
    for path, dirs, files in os.walk(source):

        curr_path = os.path.join(cwd, path)
        for directory in dirs:
            # IN FIRST ITERATION:
            # ONLY CHECK FOR WHOLE SEASONS AND MOVE TO DESIRED LOCATION
            # normalize utf-8 to NFC if needed
            directory = unicodedata.normalize('NFC', directory)
            if re.search(get_season_re, directory, re.IGNORECASE):
                if re.search(check_show_name_missing, directory, re.IGNORECASE):
                    # if current directory contains name of show, create folder and move
                    # if current directory is the source directory, do something later
                    curr_folder_name = str(Path(os.path.join(cwd, path)).name)
                    name = getName(
                        curr_folder_name, get_name_cut_on_season_re)
                    season = getNumber(directory)
                    if name != source:
                        show_path = os.path.join(
                            dest_path, name)
                        season_path = os.path.join(show_path, season)
                        os.makedirs(show_path, exist_ok=True)
                        os.makedirs(season_path, exist_ok=True)
                        # TODO:: Move content of season folder to season folder in dest
                        for filename in os.listdir(curr_path):
                            if filename == directory:
                                source_season = os.path.join(
                                    curr_path, filename)
                                for fil in os.listdir(source_season):
                                    fil_path = os.path.join(source_season, fil)
                                    moveToDest(fil, fil_path, season_path)

                    logger.debug(
                        f'TV show: {name} needs to be moved to correct')
                else:
                    name = getName(directory, get_name_cut_on_season_re)
                    season = getNumber(directory)
                    show_path = os.path.join(dest_path, name)
                    season_path = os.path.join(show_path, season)

                    os.makedirs(show_path, exist_ok=True)
                    os.makedirs(season_path, exist_ok=True)

                    source_season = os.path.join(curr_path, directory)
                    for filename in os.listdir(source_season):
                        fil_path = os.path.join(source_season, filename)
                        moveToDest(filename, fil_path, season_path)

                    logging.debug(
                        f'TV show: {name} needs to be moved to folder')
            if re.search(get_single_episode_re, directory, re.IGNORECASE | re.UNICODE):
                name = getName(directory, get_name_cut_on_episode_re)
                season = getNumber(directory)
                show_path = os.path.join(dest_path, name)
                season_path = os.path.join(show_path, season)
                os.makedirs(show_path, exist_ok=True)
                os.makedirs(season_path, exist_ok=True)

                source_season = os.path.join(curr_path, directory)
                for filename in os.listdir(source_season):
                    fil_path = os.path.join(source_season, filename)
                    moveToDest(filename, fil_path, season_path)

                logger.debug(
                    f'TV show: {name} needs to be moved to folder')
            if re.search(get_season_sequence, directory, re.IGNORECASE | re.UNICODE):
                logger.debug(
                    f'Folder: {directory} is a sequence of seasons')

    for item in os.listdir(source_path):
        item = unicodedata.normalize('NFC', item)
        if not os.path.isfile(os.path.join(source_path, item)):
            continue
        if re.search(get_episode_re, item, re.IGNORECASE):
            # print(item)
            pass
        name = getName(item, get_name_cut_on_episode_re)
        season = getNumber(item)
        if name == NAME_OR_SEASON_NOT_FOUND or season == NAME_OR_SEASON_NOT_FOUND:
            continue

        file_src = os.path.join(source_path, item)
        file_dest = os.path.join(dest_path, name, season)
        if not os.path.exists(file_dest):
            os.makedirs(os.path.join(dest_path, name), exist_ok=True)
            os.makedirs(os.path.join(dest_path, name, season), exist_ok=True)
        moveToDest(item, file_src, file_dest)

    print('--------------------------------')
    print('REPORT')
    print(f'Successfully copied {len(success)}')
    print(f'Failed: {len(failed)}')
    print('Failed shows:')
    # for show in failed:
    #     print(show)
    print('--------------------------------')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloaded Tv show Sorter")
    parser.add_argument('source', metavar='source', type=str,
                        help='Source of the folder containing all the tv shows')
    parser.add_argument('dest', metavar='destination', type=str,
                        help='Destination where sorted tv shows should end')
    args = parser.parse_args()

    main(args.source, args.dest)
