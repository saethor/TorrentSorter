#! /usr/bin/env python

import os
import re
import shutil
import unicodedata
import argparse
import logging
import platform
from pathlib import Path


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
get_season_re = r'(sería|season|series) *\.?\d\d?(?! *\d?\-)|(?<!\d)\d\d?\. *(season|sería|series)|(S\d\d?(?!\w))|^\d\d?$'
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

# Common leftovers that needs to be removed from names
IRL = 'Irl'
CA = 'Ca'
THE_COMPLETE = 'The Complete'
COMPLETE = 'complete'
UK = '(Uk)'
TORRENT_DAY = 'Torrentday'

extensions = ['avi', 'mp4', 'mov', 'mpg', 'mkv', 'm4v', 'wmv']


def moveToDest(fil, source, dest):
    '''Moves file from source to correct destination'''
    ext = fil.split('.')[-1]
    if ext.lower() not in extensions:
        return

    if not os.path.isdir(source):
        try:
            shutil.copy(source, dest)
            success.append(fil)
            logger.debug(f'Copied file {source} to {dest}')
        except FileNotFoundError:
            failed.append(fil)
            logger.debug(f'Failed to copy file {source}')


def cleanName(name):
    '''Helper function that is ment for some edge cases
    ideally this is the only function that needs to be improved over time
    '''
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

    illegal = ['_', '-', '.', ',', '(', ')', '[', ']']
    for i in illegal:
        if i in name:
            name = name[:name.find(i)]
    return name.title()


def getName(directory, regex):
    '''Abstracts season name from directory/file name'''
    name = re.search(regex, directory, re.IGNORECASE)
    if name:
        name = name.group()
        show_name = name.split('.')

        if len(show_name) == 1:
            show_name = name.split('-')

        show_name = ' '.join(show_name)

        show_name = cleanName(show_name)
        return show_name.strip()
    else:
        return cleanName(directory)


def getNumber(directory):
    '''Function that extracts the season number from the folder name'''
    number = re.search(get_season_number, directory, re.IGNORECASE)
    if number:
        season = number.group().strip()
        season = season.replace('S', '')
        season = season.replace('s', '')
        season = season.zfill(2)
        return f'Season {season}'
    elif directory.isdigit():
        season = directory.zfill(2)
        return f'Season {season}'
    else:
        return False


def create_show_and_season_folder(name, season, dest_path):
    '''Creates show and season directory in destination path'''
    if not season:
        return
    show_path = os.path.join(dest_path, name)
    season_path = os.path.join(show_path, season)
    os.makedirs(show_path, exist_ok=True)
    os.makedirs(season_path, exist_ok=True)


def show_and_season_worker(directory, regex, curr_path, dest_path):
    '''Removed duplicated code in main, gets show name and season number, created directory and moves files'''
    name = getName(directory, regex)
    season = getNumber(directory)
    create_show_and_season_folder(name, season, dest_path)
    source_season = os.path.join(curr_path, directory)
    if directory == "House.of.Cards.Season.4.720p.WEBRiP.x265.ShAaNiG":
        print(name)
        print(season)
        print(source_season)
    for filename in os.listdir(source_season):
        fil_path = os.path.join(source_season, filename)
        moveToDest(filename, fil_path, os.path.join(
            os.path.join(dest_path, name), season))


def main(source, dest):
    '''Finds tv shows and organizes them'''
    # Check if source folder exists
    if not os.path.isdir(source):
        raise ValueError(
            'Invalid arguments\nRun clean.py <source_folder> <destination_folder>')

    if not os.path.isdir(dest):
        os.makedirs(dest)

    # CWD
    cwd = os.getcwd()

    # source path as string and Pathlib object
    source_path = os.path.join(cwd, source)

    # destination path as string and Pathlib object
    dest_path = os.path.join(cwd, dest)

    for path, dirs, files in os.walk(source):
        curr_path = os.path.join(cwd, path)
        for directory in dirs:
            directory = unicodedata.normalize('NFC', directory)
            if re.search(get_season_re, directory, re.IGNORECASE):
                if re.search(check_show_name_missing, directory, re.IGNORECASE):
                    # if current directory contains name of show, create folder and move
                    # if current directory is the source directory, do something later
                    curr_folder_name = str(Path(os.path.join(cwd, path)).name)
                    name = getName(
                        curr_folder_name, get_name_cut_on_season_re)
                    season = getNumber(directory)
                    if name != source.title():
                        create_show_and_season_folder(name, season, dest_path)
                        for filename in os.listdir(curr_path):
                            if filename == directory:
                                source_season = os.path.join(
                                    curr_path, filename)
                                for fil in os.listdir(source_season):
                                    fil_path = os.path.join(source_season, fil)
                                    moveToDest(fil, fil_path, os.path.join(
                                        os.path.join(dest_path, name), season))
                else:
                    print(directory)
                    show_and_season_worker(
                        directory, get_name_cut_on_season_re, curr_path, dest_path)

            elif re.search(get_single_episode_re, directory, re.IGNORECASE | re.UNICODE):
                show_and_season_worker(
                    directory, get_name_cut_on_episode_re, curr_path, dest_path)

    for item in os.listdir(source_path):
        item = unicodedata.normalize('NFC', item)
        if not os.path.isfile(os.path.join(source_path, item)):
            continue

        name = getName(item, get_name_cut_on_episode_re)
        season = getNumber(item)

        if not name or not season:
            continue

        create_show_and_season_folder(name, season, dest_path)
        file_src = os.path.join(source_path, item)
        file_dest = os.path.join(dest_path, name, season)
        moveToDest(item, file_src, file_dest)

    logger.debug(f'''
        REPORT
        ------
            Successfully copied {len(success)}
            Failed {len(failed)}
    ''')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Downloaded Tv show Sorter")
    parser.add_argument('source', metavar='source', type=str,
                        help='Source of the folder containing all the tv shows')
    parser.add_argument('dest', metavar='destination', type=str,
                        help='Destination where sorted tv shows should end')
    args = parser.parse_args()

    main(args.source, args.dest)
