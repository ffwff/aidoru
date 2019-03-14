from functools import total_ordering
import datetime
import taglib
from .utils import *

@total_ordering
class MediaInfo(object):

    def __init__(self, path, pos, title, artist, album, albumArtist, duration, image, year=0):
        self.path = path
        self.pos = pos
        self.title = title
        self.artist = artist
        self.album = album
        self.albumArtist = albumArtist
        self.year = year
        self.duration = duration
        self.image = image

    def fromFile(path):
        try:
            song = taglib.File(path)
        except OSError:
            return None
        artist = song.tags["ARTIST"][0] if "ARTIST" in song.tags else ""
        title = song.tags["TITLE"][0] if "TITLE" in song.tags else os.path.basename(path)
        searchPath = pathUp(path)
        # find cover art
        paths = list(filter(lambda path: getFileType(path) == "image", os.listdir(searchPath)))
        if paths:
            prioritize = ["Case Cover Back Outer", "Cover.", "cover.", "CD."]
            def find_path():
                for path in paths:
                    for priority in prioritize:
                        if path.startswith(priority):
                            return path
                return paths[0]
            imagePath = find_path()
        else:
            imagePath = None
        pos = -1
        if "TRACKNUMBER" in song.tags:
            try:
                if "/" in song.tags["TRACKNUMBER"][0]:
                    pos = int(song.tags["TRACKNUMBER"][0].split("/")[0])
                else:
                    pos = int(song.tags["TRACKNUMBER"][0])
            except ValueError:
                pass
        album = song.tags["ALBUM"][0] if "ALBUM" in song.tags else ""
        albumArtist = song.tags["ALBUMARTIST"][0] if "ALBUMARTIST" in song.tags else artist
        try:
            year = int(song.tags["DATE"][0])
        except:
            year = -1
        return MediaInfo(path, pos, title, artist,
                         album, albumArtist,
                         datetime.datetime.fromtimestamp(song.length),
                         os.path.join(searchPath, imagePath) if imagePath else None,
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
        if os.path.samefile(self.path, other.path):
            return True
        return object.__eq__(self, other)
