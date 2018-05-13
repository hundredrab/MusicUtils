# MusicUtils
Library to download music from list of songs (and websites such as billboards.com) and updating their metadata (Title, TrackNo, Artist, Album, AlbumArt, Lyrics etc.) **Under Construction**

## Installation

Make sure you're using `python3`.

### Requirements:

`sudo apt install ffmpeg`

`sudo apt install youtube-dl`


### Clone the repository

`git clone https://github.com/hundredrab/MusicUtils.git`

Navigate into the project directory

`cd MusicUtils`

### Installing dependencies

`pip install requests bs4 mutagen eyed3`

`pip install lxml`


## Usage

Use 

`python utils.py "Song Item 1" "Song Item 2" "Song Item 3" [...]` 

to download individual files.

Use 

`python utils.py -f "songlist.txt"`

to download files using a text file containing song titles in individual lines.
`songlist.txt` is a list of song title-artist pairs, one in a line.
