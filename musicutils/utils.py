#!/usr/bin/env python3
try:
    import argparse
    import bs4
    import eyed3
    import os
    import re
    import requests
    import youtube_dl
    from mutagen import File
    from mutagen.id3 import ID3, APIC, _util, USLT
    from mutagen import File
    from mutagen.mp3 import EasyMP3
except ModuleNotFoundError:
    print("Couldn't import all the requirements. Maybe reinstall musicutils?\n\n")
    raise
# import sysargs

global DOWNLOADED_FILE
global verbose

verbose = True


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
    'outtmpl': "music_new/%(title)s-%(id)s.%(ext)s",
    'noplaylist': True,    # only download single song, not playlist
    'quiet': True,  # Don't print anything
    'no_warnings': True,
    'forcefilename': True,
    'progress_hooks': [my_hook],
    'restrictfilenames': True,
}


def Wrapper():
    """
    The main function, handles all command line arguments etc.
    """

    # TODO: This should properly handle the following, in addition to the flags:
    # Default: A single song name in the format '{artist} - {song}'.
    # Urls- Billboards and Top Tens at the least.
    # Keywords for billboards genres.
    # Filepaths for list of songs to download.
    # Repair only: Accept a filepath and only repair the metadata of the songs there.
    pass


def main():
    """
    Initialize as global variable the settings as found in the config file and the command-line arguments.
    """
    # global DetailsFlag, ExtendedFlag, IgnoreDownloadedFlag, NoDownloadedAddFlag, OutPath, DownloadedListPath
    global done_list
    done_list = []
    parser = argparse.ArgumentParser()
    parser.add_argument("titles", type=str, nargs='*',
                        help="All the names separated by a space will be \
                        searched and downloaded.")
    parser.add_argument("-f", "--file", type=str,
                        help="Specify the file name, to download using \
                        reference as.")
    parser.add_argument("-u", "--url", type=str,
                        help="Specify the url where list is located.")
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

    args = parser.parse_args()
    if args.url:
        print("You want an url:", args.url)
    if args.titles:
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


def GetMusicFromList(queue, IgnoreDownloadedFlag, NoDownloadedAddFlag):
    """
    For each item in each line in list,
    downloads the music file if not already downloaded and adds that to the
    DOWNLOADED file list.
    """

    '''Remove next 3.'''
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
            (art, title) = GetBasicDetails(song)
            if not ExtendedFlag:
                extDetail = GetExtendedDetails(song)  # A dictionary
                UpdateDetails(DOWNLOADED_FILE, extDetail)
            else:
                UpdateDetails(audio, {'artist': art, 'title': title})
        if not NoDownloadedAddFlag:
            # So that this file won't be downloaded again.
            AddToDownloaded(song)


def GetListFromURL(url):
    """
    Return a list of strings containing song details after processing the URL.

    The URL is expected to be a billboards or a top-tens url.
    """
    pass


def GetListFromFile(path):
    """
    Return a list of strings containing song details extracted from a file.

    The songs are supposed to be in individual lines, preferably
    in the format '{artist} - {song}'.
    """
    pass


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
    """
    Return the artist and title of the song.
    """
    # TODO: Use RE to return the artist, title combination extracted from list.
    return ('artist', 'title')


def GetExtendedDetails(song):
    """Returns full details of song."""
    details = {}
    res = requests.get("https://www.google.co.in/search?q=genius " + song)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    try:
        link = soup.select('.r a')[0].get('href')

        res2 = requests.get("https://google.com" + link)
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
