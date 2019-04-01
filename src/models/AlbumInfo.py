from functools import total_ordering
from src.utils import pathUp, getFileType
from .MediaInfo import MediaInfo
import os

@total_ordering
class AlbumInfo(object):

    def __init__(self, info, populate=True):
        self.medias = []
        if isinstance(info, str):
            self.title = info
            self.path = info
            self.artist = self.image = None
        else:
            self.title = info.album
            self.path = pathUp(info.path)
            self.artist = info.albumArtist
            self.image = info.image

            if populate:
                for f in os.listdir(self.path):
                    fpath = os.path.join(self.path, f)
                    if os.path.isfile(fpath) and getFileType(fpath) == "audio":
                        mediaInfo = MediaInfo.fromFile(fpath)
                        self.medias.append(mediaInfo)
                self.medias.sort()

    def __lt__(self, other):
        return self.title < other.title
