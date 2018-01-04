import os
import re
from mutagen import File
# import sysargs


def Wrapper():
    """ 
    The main function, handles all command line arguments etc.
    """

    # TODO: This shoudl properly handle the following, in addition to the flags:
    # Default: A single song name in the format '{artist} - {song}'.
    # Urls— Billboards and Top Tens at the least.
    # Keywords for billboards genres.
    # Filepaths for list of songs to download.
    # Repair only: Accept a filepath and only repair the metadata of the songs there.
    pass


def InitConfig():
    """
    Initialize as global variable the settings as found in the config file and the command-line arguments.
    """
    global DetailsFlag, ExtendedFlag, IgnoreDownloadedFlag, NoDownloadedAddFlag, OutPath, DownloadedListPath
    pass


def GetMusicFromList(queue):
    """
    For each item in each line in list,
    downloads the music file if not already downloaded and adds that to the
    DOWNLOADED file list.
    """
    for song in queue:
        if song in downloaded and not IgnoreDownloadedFlag:
            continue
        audio = Download(song)
        if not DetailsFlag:
            (art, title) = GetBasicDetails(song)
            if not ExtendedFlag:
                extDetail = GetExtendedDetails(art, title)  # A dictionary
                UpdateDetails(audio, extDetail)
            else:
                UpdateDetails(audio, {'artist': art, 'title': title})
        if not NoDownloadedAddFlag:
            # So that this file won't be downloaded again.
            AddToDownloaded(song)


def GetListFromURL(url):
    """
    Return a list of strings containing song details after processing the URL. The URL is expected to be a billboards or a top-tens url.
    """
    pass


def GetListFromFile(path):
    """
    Return a list of strings containing song details extracted from a file. The songs are supposed to be in individual lines, preferably
    in the format '{artist} - {song}'.
    """
    pass


def Download(song):
    """
    Download a song using Youtube-dl and return it's file path.
    """
    pass


def GetBasicDetails(song):
    """
    Return the artist and title of the song. 
    """
    # TODO: Use RE to return the artist, title combination extracted from list.
    return (artist, title)


def UpdateDetails(audio, details):
    """
    Update the metadata of the files.
    """
    pass


def AddToDownloaded(song):
    """
    Append the song at the end of the file which stores the list of downloaded files
    so they won't be downloaded again.
    """
    pass
