#!/usr/bin/env python3
import argparse
import logging
import os
import re
import sys
from os.path import expanduser

import bs4
import eyed3
import youtube_dl
from mutagen import File
from mutagen.id3 import APIC, ID3, USLT, _util
from mutagen.mp3 import EasyMP3

import requests
import yaml

global DOWNLOADED_FILE
global verbose
global CONFIG_FILE
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name) - 12s %(levelname) -8s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

verbose = True

home = expanduser("~")
CONFIG_FILE = home + "/musicutils.yaml"

# If default conf file does not exist, create it
if not os.path.exists(os.path.dirname(CONFIG_FILE)):
    os.makedirs(os.path.dirname(CONFIG_FILE))
    with open(CONFIG_FILE, 'a') as f:
        pass
    logger.debug("Created new config file at %s", CONFIG_FILE)

# logger.debug("Config: %s", conf)


def my_hook(d):
    if d['status'] == 'finished':
        global DOWNLOADED_FILE
        if '.webm' in d['filename']:
            DOWNLOADED_FILE = d['filename'][:-4]+'mp3'
        else:
            DOWNLOADED_FILE = d['filename'][:-3]+'mp3'


ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'outtmpl': "%(title)s-%(id)s.%(ext)s",
    'noplaylist': True,    # only download single song, not playlist
    'quiet': False,
    'no_warnings': True,
    'forcefilename': True,
    'progress_hooks': [my_hook],
    'restrictfilenames': True,
    'nocheckcertificate': True,
    # 'default_search': 'auto',
}


def main():
    """
    Initialize as global variable the settings as found in the config file and the command-line arguments.
    """
    global done_list
    global CONFIG_FILE
    done_list = []
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("titles", type=str, nargs='*',
                        help="All the names separated by a space will be \
                        searched and downloaded.")
    parser.add_argument("-f", "--file", type=str,
                        help="Specify the file name, to download using \
                        reference as.")
    parser.add_argument("-u", "--url", type=str,
                        help="Specify the url where list is located.")
    parser.add_argument("-k", "--keyword", type=str,
                        help="Add additional keywords for search.")
    parser.add_argument("-n", "--count", type=int,
                        help="Number of files to download from playlist/url.")
    parser.add_argument("-r", "--repair_only", action="store_true",
                        help="Skip downloading and only add metadata.")
    parser.add_argument("--ignore_downloaded", action="store_true",
                        help="Skip checking the downloaded.txt and \
                        download all files.")
    parser.add_argument("--no_downloaded", action="store_true",
                        help="Skip adding the downloaded files to \
                        downloaded.txt.")
    parser.add_argument("-c", "--config", type=str,
                        help="Specify config file.")
    parser.add_argument("--ignore-config", action="store_true",
                        help="Ignore the default config file.")
    parser.add_argument("--arrange", '-a', action="store_true",
                        help="Rearrange directory into artsit->album folder.")
    parser.add_argument("--directory", "-d", type=str,
                        help="Specify a directory.")

    # Check if arguments have a config file and use that.
    args_temp = parser.parse_args()
    if args_temp.config:
        CONFIG_FILE = args_temp.config

    if os.path.exists(CONFIG_FILE):
        logging.debug("Using config file.")
        sys.argv = ['@'+CONFIG_FILE] + sys.argv
    else:
        logging.debug("No conf file found at %s", CONFIG_FILE)
    args = parser.parse_args(sys.argv)
    logger.debug("ARGV: %s", sys.argv)

    logger.debug("ARGUMENTS SUPPLIED: %s", str(args))

    if args.directory and os.path.exists(args.directory):
        ydl_opts['outtmpl'] = os.path.join(args.directory, ydl_opts['outtmpl'])
        logger.debug("Output path: %s", ydl_opts['outtmpl'])

    if args.arrange:
        if not args.directory:
            print("Need a directory to rearrange. Supply one with '-d' or '--directory'.")
            logger.debug("Directory not supplied, rearrangement failed.")
        else:
            logger.debug("Arranging in the direcotory: %s", args.directory)
            Rearrange(args.directory)
            logger.debug("Rearrangement finished.")

    if args.url:
        print("You want an url:", args.url)
        if 'thetoptens' in args.url:
            if args.count:
                GetTopTensMusic(args.url, args.keyword, args.count)
            else:
                GetTopTensMusic(args.url, args.keyword)

        if 'billboard' in args.url:
            if args.count:
                GetBillboardsMusic(args.url, args.count)
            else:
                GetBillboardsMusic(args.url)
        if 'youtube.com' in args.url:
            GetYoutubeMusic(args.url)

    args.titles = args.titles[1:]
    if args.titles:
        logger.debug("Getting titles: %s", args.titles)
        GetMusicFromList(args.titles, args.ignore_downloaded,
                         args.no_downloaded)

    if args.file:
        try:
            with open(args.file) as f:
                tbd = f.readlines()
                GetMusicFromList(tbd, args.ignore_downloaded,
                                 args.no_downloaded)
        except FileNotFoundError:
            print("The specified file was not found.")
            print("Are you sure " + args.file + " exists here?")


def Rearrange(dir):
    files = os.listdir(dir)
    files = [_ for _ in files if _.endswith('.mp3') or _.endswith(
        '.m4a') or _.endswith('mp4') or _.endswith(
        '.wav') or _.endswith('.webm')]
    print("Found " + str(len(files)) + " files in "+dir+".")
    for audio in files:
        try:
            f = EasyMP3(dir+"/"+audio)
            artist = f["artist"][0]
            if artist == "" or artist == "Unknown":
                artist = "unknown"
            album = f["album"][0]
            if album == "" or album == "Unknown":
                album = "unknown"

            if not os.path.exists(dir+"/"+artist):
                os.makedirs(dir+"/"+artist)
            if not os.path.exists(dir+"/"+artist+"/"+album):
                os.makedirs(dir+"/"+artist+"/"+album)
            os.rename(dir+"/"+audio, dir+"/"+artist+"/"+album+"/"+audio)
        except:
            print("Skipping file " + dir+"/"+audio)


def GetTopTensMusic(url, keyword, count=10):
    if not keyword:
        keyword = ''
    logger.debug(
        "Getting top %s titles from the url %s with the keyword: %s", count, url, keyword)
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    songs = soup.select('.i b')
    songs = [i.getText() + ' ' + str(keyword) for i in songs]
    songs = songs[:count]
    logger.debug("Found titles: %s", songs)
    print("Getting " + str(len(songs)) + " songs from the url.")
    GetMusicFromList(songs, False, False)


def GetYoutubeMusic(url):
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([str(url)])
    logger.debug("Result for Youtube-url download %s", result)
    AddToDownloaded(url)


def GetBillboardsMusic(url, count=10):
    res = requests.get(url, "lxml")
    soup = bs4.BeautifulSoup(res.text, "lxml")
    song_rows = soup.select('.chart-list-item')
    music = []
    for song in song_rows:
        song_tup = tuple([song.select('.chart-list-item__title-text')[0].getText().strip(), song.select(
            '.chart-list-item__artist')[0].getText().strip()])
        music.append(song_tup[1] + ' - ' + song_tup[0])
    GetMusicFromList(music[:count], False, False)


def GetMusicFromList(queue, IgnoreDownloadedFlag, NoDownloadedAddFlag):
    """
    For each item in each line in list,
    downloads the music file if not already downloaded and adds that to the
    DOWNLOADED file list.
    """

    '''Remove next 3.'''
    print(len(queue))
    logger.debug("Queud up: %s", queue)
    downloaded = []
    DetailsFlag = False
    ExtendedFlag = False
    for song in queue:
        if song in downloaded and not IgnoreDownloadedFlag:
            continue
        try:
            Download(song)
        except youtube_dl.DownloadError:
            print("\nInstall ffmpeg to download in the specified format.")
            print("Exiting prematurely.")
            break
        audio = DOWNLOADED_FILE
        if not DetailsFlag:
            # (art, title) = GetBasicDetails(song)
            if not ExtendedFlag:
                extDetail = GetExtendedDetails(song)  # A dictionary
                UpdateDetails(DOWNLOADED_FILE, extDetail)
            else:
                UpdateDetails(audio, {'artist': art, 'title': title})
        if not NoDownloadedAddFlag:
            # So that this file won't be downloaded again.
            AddToDownloaded(song)


def Download(song):
    """
    Download a song using Youtube-dl and return it's file path.
    """
    done_list = []
    if song.strip() not in done_list:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            resutl = ydl.download(['ytsearch:' + str(song)])
            # print(result)
        AddToDownloaded(song)


def GetBasicDetails(song):
    return None


def GetExtendedDetails(song):
    """Returns full details of song."""
    details = {}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) '
                             'Gecko/20100101 Firefox/12.0'
              }

    res = requests.get(
        "https://www.google.co.in/search?q=genius " + song,
        headers=headers
    )
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    print("we're soup-y")
    try:
        link = soup.select('.r a')[0].get('href')
        print("links:", link)

        res2 = requests.get(link)
        soup = bs4.BeautifulSoup(res2.text, 'lxml')

        infos = soup.select('.metadata_unit-info a')
        for info in infos:
            if 'albums' in info.get('href'):
                details['album'] = info.getText().strip()
                break
        details['title'] = soup.select('h1')[0].getText().strip()
        details['artist'] = soup.select('h2')[0].getText().strip()
        details['album_art'] = soup.select('.cover_art img')[0].get('src')

        lyrics = soup.select('.lyrics')
        l = ""
        for lyr in lyrics:
            l += lyr.getText()
        details['lyrics'] = l
        print("\n\n\n\n")
        return details
    except IndexError:
        print("Error gettings details. Skipping this part")
        return details


def UpdateDetails(audio, details):
    """
    Update the metadata of the files.
    """
    keys = details.keys()

    print("Updating metadata for " + audio)

    if 'album_art' in keys:
        img = requests.get(details['album_art'], stream=True)
        img = img.raw
        file = File(audio)
        try:
            file.add_tags()
        except _util.error:
            pass
        file.tags.add(
            APIC(
                encoding=3,  # UTF-8
                mime='image/png',
                type=3,  # 3 is for album art
                desc='covr',
                data=img.read()  # Reads and adds album art
            )
        )
        file.save()
    file = EasyMP3(audio)
    if 'artist' in keys:
        file["artist"] = (details['artist'])
        file["albumartist"] = details['artist']
    if 'title' in keys:
        file["title"] = details['title']
    if 'album' in keys:
        file["album"] = details['album']
    file.save()
    print("Current tags:", file.tags)

    file = ID3(audio)
    if 'lyrics' in keys:
        file[u"USLT::'en'"] = (
            USLT(encoding=3, lang=u'eng', desc=u'desc', text=details['lyrics'])
        )
        file.save()
    print("Done!")


def AddToDownloaded(song):
    """
    Append the song at the end of the file which stores the list of downloaded files
    so they won't be downloaded again.
    """
    pass


if __name__ == "__main__":
    main()
