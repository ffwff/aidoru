from PyQt5.QtCore import QUrl
from functools import total_ordering
import datetime
import taglib
import os
from hashlib import md5
from src.utils import getFileType, pathUp, imageMimetypeToExt
from src.models.Database import Database

@total_ordering
class MediaInfo(object):

    IMAGE_CACHE = os.path.join(Database.BASE, "cache")

    def __init__(self, path,
                       pos=0,
                       title="", artist="",
                       album="", albumArtist="",
                       duration=datetime.datetime.fromtimestamp(0),
                       image=None, year=0):
        self.path = path
        self.pos = pos
        self.title = title if title else path
        self.artist = artist
        self.album = album
        self.albumArtist = albumArtist
        self.year = year
        self.duration = duration
        self.image = image

    def searchImage(path, song=None):
        if song and song.picture:
            picture = song.picture
            ext = imageMimetypeToExt(picture.mimetype)
            dataHash = md5(picture.data).hexdigest()
            fpath = os.path.join(MediaInfo.IMAGE_CACHE, dataHash + ext)
            if os.path.isfile(fpath): return fpath
            Database.saveFile(picture.data, dataHash + ext, "cache")
            return fpath

        searchPath = pathUp(path)
        paths = list(filter(lambda path: getFileType(path) == "image", os.listdir(searchPath)))
        if paths:
            prioritize = ["Case Cover Back Outer", "Cover.", "cover.", "CD."]
            def find_path():
                for path in paths:
                    for priority in prioritize:
                        if path.startswith(priority):
                            return path
                return paths[0]
            return os.path.join(searchPath, find_path())
        else:
            return None

    def verify(self):
        if not os.path.isfile(self.path):
            return False
        if self.image and not os.path.isfile(self.image):
            self.image = MediaInfo.searchImage(self.path)
        return True

    def fromFile(path):
        try:
            song = taglib.File(path)
        except OSError:
            return MediaInfo(QUrl.fromLocalFile(path).toString(), 0, os.path.basename(path))
        artist = song.tags["ARTIST"][0] if "ARTIST" in song.tags else ""
        title = song.tags["TITLE"][0] if "TITLE" in song.tags else os.path.basename(path)

        pos = -1
        if "TRACKNUMBER" in song.tags:
            try:
                if "/" in song.tags["TRACKNUMBER"][0]:
                    pos = int(song.tags["TRACKNUMBER"][0].split("/")[0])
                else:
                    pos = int(song.tags["TRACKNUMBER"][0])
            except ValueError:
                pass

        try: album = song.tags["ALBUM"][0]
        except: album = ""

        try: albumArtist = song.tags["ALBUMARTIST"][0]
        except: albumArtist = artist

        try: year = int(song.tags["DATE"][0])
        except: year = -1

        return MediaInfo(QUrl.fromLocalFile(path).toString(), pos, title, artist,
                         album, albumArtist,
                         datetime.datetime.fromtimestamp(song.length),
                         MediaInfo.searchImage(path, song),
                         year)

    # comparators
    def __lt__(self, other):
        if not isinstance(other, MediaInfo):
            return False
        if self.album == other.album and self.pos != -1 and other.pos != -1:
            return self.pos < other.pos
        return self.title < other.title

    def __eq__(self, other):
        if not isinstance(other, MediaInfo):
            return False
        if self.path == other.path:
            return True
        return object.__eq__(self, other)
