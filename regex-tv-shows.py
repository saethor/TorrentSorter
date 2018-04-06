import re

# NEWER REGEX

# Folder that is a season
r'(sería|season|series) *\d\d?(?! *\d?\-)|(?<!\d)\d\d?\. *(season|sería|series)|(S\d\d?(?!\w))'

# If folder is contains only season and number
r'(?<![ \d\w.])(\d\d?\. *(season|sería|series))|(?<![ \d\w.])(season|sería|series) *\d\d?|(?<![ \d\w.])S\d\d?(?![-])'

# Get name of TV show
r'(.*)((?= *season|series|sería|S\d\d?|\.\d))'

# Get number of season

# OLDER REGEX
# Folder that is a single season IGNORES the keyword 'series'
r'((sería)|(season)) *\d\d?(?!\-| \-)|(S\d\d?(?![\d\w]))|(?<!\d)(\d\d?[ .]*((season)|(sería)))'

# Check if folder only contains season and number
r'(?<![ \d\w.])(\d\d?\. *(season|sería))|(?<![ \d\w.])(season|sería) *\d\d?|(?<![ \d\w.])S\d\d?(?![-])'


# find name of show
r'([\w\d \-\)\(\.]*)((?= \d\d?. sería))|([\w\d \-\)\(\.]*)((?= *season))|([\w\d \-\)\(\.]*)((?= *sería))|([\w\d \-\)\(\.]*)((?=\.\d\d\d\.))|([\w\d \-\)\(\.]*)((?= *S\d))'
# Find the number of season
r'S\d\d?|(?<=season|sería|series\s)\d\d?'


# TEST STRING

Community.S04.
Magic's Biggest Secrets Finally Revealed season 10
testseason 7 2313.2
test season 7 2313.2
season test season 7 2313.2
testing sería 10.
8 Out of 10 Cats - Season 7
[www.TorrentDay.com] - Spy.2011.S01E02.HDTV.XviD-TLA
[www.TorrentDay.com] - Spy.2011. season 10
Spy.2011. season 10
8.Out.Of.10.Cats.S15E02.HDTV.x264-TLA
Arrested Development 4. sería - fyrstu 10
Body.of.Proof.S02E01.HDTV.XviD-LOL.[VTV]
desperate.housewives.803.hdtv-lol
Modern Family Season 1-7
Modern Family Season 1 - 7
Raising Hope S01
Dexter Season2-25
New.Girl.S02.Complete.720p.HDTV.ReEnc-[maximersk]
Season 12
Californication S07E1-9
Californication S07E1 - 9
Dragons Den S2
Just a minute series 12-14
Dragons Den(UK) Season 6


# Folder that is a sequence of seasons
r'((series)|(sería)|(season))\s*\d\d?\s*\-\s*\d\d?|S\d{2}e\d\d?\s*\-\s*\d\d?'

# Folder that is a single episode
r'S\d{2}E\d{2}'
