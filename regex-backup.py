
# extract season name from folder
get_name_cut_on_season_re = r'(.*)((?= *season|series|sería))|(.*)((?=.S\d\d?))|(.*)((?= *S\d\dE\d\d))'
# extract season name from folder
get_name_cut_on_episode_re = r'(.*)((?= *S\d\dE\d\d))'

# extract season name from single file
get_name_from_file_re = r'(.*)((?= *season|series|sería|S\d\d?|\.\d|\d\d?x\d\d?))'

# regex for the number of the season
get_season_number = r'S\d\d?|(?<=season) *\.?\d\d?|S\d\d?|(?<=sería) *\.?\d\d?|S\d\d?|(?<=series) *\.?\d\d?|(?<!\d)\d\d?(?=\. *season)|(?<!\d)\d\d?(?=\. *sería)|(?<!\d)\d\d?(?=\. *series)|^\d\d?$'

# regex to get the season and number as it is from the file or folder name
get_original_season_and_number = r'(season|sería|series) *\d\d?|\d\d? *\. *(season|sería|series)'

# regex for finding a season
get_season_re = r'(sería|season|series) *\.?\d\d?(?! *\d?\-)|(?<!\d)\d\d?\. *(season|sería|series)|(S\d\d?(?!\w))|^\d\d?$'
# helper sub-regex to determine if the name of a season folder does not contain the name of the show, then the current directory needs to be reviewed
check_show_name_missing = r'(?<![ \d\w.])(\d\d?\. *(season|sería|series))|(?<![ \d\w.])(season|sería|series) *\.?\d\d?|(?<![ \d\w.])S\d\d?(?![-])|^\d\d?$'

# regex for finding an episode
get_episode_re = r'\d\d?x\d\d?|s\d\d?e\d\d?|\.\d\d\d?\.|(season|series|sería) *[\w\d] *(episode|þáttur) *[\d\w]'


# regex for finding single episode as folder or file
get_single_episode_re = r'S\d\d?E\d\d'

# regex to find a folder containing a sequence of seasons
get_season_sequence = r'(series|season|sería|S\d\d?E) *\d\d? *\- *\d\d? *'


# Specific regexes for some edge cases

uk_re = r'(.*)((?= \(Uk))'
year_re = r'(19|20)\d{2}'
