# MusicUtils
Library to download music from list of songs (and websites such as billboards.com) and updating their metadata (Title, TrackNo, Artist, Album, AlbumArt, Lyrics etc.) **Under Construction**

## Installation

Make sure you're using `python3` and have `pip` installed and enabled.

### Requirements:

**On a linux system:**

`sudo apt install ffmpeg`

`sudo apt install youtube-dl`

**On windows:**

`pip install youtube-dl`

Installing ffmpeg is slightly trickier. [Read the instructions here](http://adaptivesamples.com/how-to-install-ffmpeg-on-windows/). 


**On MacOS**

`brew install ffmpeg`

`brew link ffmpeg`

`brew install youtube-dl`


### Clone the repository

`git clone https://github.com/hundredrab/MusicUtils.git`

Navigate into the project directory

`cd MusicUtils`

### Installing dependencies

`pip install requests bs4 mutagen eyed3 lxml`


## Usage

Use 

`python utils.py "Song Item 1" "Song Item 2" "Song Item 3" [...]` 

to download individual files.

Use 

`python utils.py -f "songlist.txt"`

to download files using a text file containing song titles in individual lines.
`songlist.txt` is a list of song title-artist pairs, one in a line.
