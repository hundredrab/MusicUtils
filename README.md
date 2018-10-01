# MusicUtils
Library to download music from list of songs (and websites such as billboards.com) and updating their metadata (Title, TrackNo, Artist, Album, AlbumArt, Lyrics etc.) //**In development**

## Installation

Make sure you're using `python3` and have `pip` installed and enabled. On the command line, simply run:

`pip install musicutils`

### Requirements:

MusicUtils requires ffmpeg to convert files to mp3.

**On a linux system:**

`sudo apt install ffmpeg`

**On windows:**

Installing ffmpeg is slightly trickier on windows. [Read the instructions here](http://adaptivesamples.com/how-to-install-ffmpeg-on-windows/). 


**On MacOS**

`brew install ffmpeg`

`brew link ffmpeg`

## Usage

MusicUtils can be invoked from the commandline after installation.  

`mutils "Song Item 1" "Song Item 2" "Song Item 3" [...]` 

to download individual files.

For example, 

`mutils "A Great Big World - Say Something"`

Use  `mutils -f "songlist.txt"` to download files using a text file containing song titles in individual lines.

`songlist.txt` is a list of song title-artist pairs, one in a line.

You may also replace a song title by it's incomplete lyrics, and in most cases, it should work just fine.

In case of weird results, remember that the first result on Youtube is what is downloaded.

**Downloading songs from a list in a url**

`mutils --url https://www.thetoptens.com/indie-rock-songs/ --count 20`

OR

`mutils -u https://www.thetoptens.com/indie-rock-songs/ -n 20`

Count is optional, defaults to *10*.

*Supported list sites:*
- https://www.thetoptens.com/

## Manual installation of the project

Clone the repository

`git clone https://github.com/hundredrab/MusicUtils.git`

Navigate into the project directory

`cd MusicUtils`

Install musicutils and its dependencies

`python setup.py install`


