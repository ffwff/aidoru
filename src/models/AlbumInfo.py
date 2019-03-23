from functools import total_ordering
from src.utils import pathUp

@total_ordering
class AlbumInfo(object):

    def __init__(self, info):
        if isinstance(info, str):
            self.title = info
            self.path = info
            self.artist = self.image = None
        else:
            self.title = info.album
            self.path = pathUp(info.path)
            self.artist = info.albumArtist
            self.image = info.image
        self.medias = []

    def __lt__(self, other):
        return self.title < other.title
