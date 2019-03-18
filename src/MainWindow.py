from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
import sys
import os
import urllib.parse
from .Database import Database
from .MediaInfo import MediaInfo
from .views.PlayerWidget import PlayerWidget
from .views.MediaPlayer import MediaPlayer
from .utils import *

class MainWindow(QMainWindow):

    # modes
    FULL_MODE = 0
    MINI_MODE = 1
    MICRO_MODE = 2

    # settings
    DEFAULT_SETTINGS = {
        "mediaLocation": os.path.expanduser("~/Music"),
        "fileWatch": True
    }
    SETINGS_FILE = "settings.json"
    MEDIAS_FILE = "medias.pkl"

    # main
    def __init__(self):
        QMainWindow.__init__(self)

        self.setAcceptDrops(True)

        self.media = QMediaPlayer()
        self.mediaInfo = None
        self.album = []
        self.albumPath = ""
        self.medias = [] # medias in scan directory
        self.settings = Database.load(MainWindow.SETINGS_FILE, True,
                                      MainWindow.DEFAULT_SETTINGS)
        self.setWatchFiles()

    def initUI(self):
        self.setWindowTitle("aidoru~~")
        self.mode = None
        self.setMode(MainWindow.FULL_MODE)
        self.setStyleSheet(Database.loadFile("style.css", "style.css"))

        # events
        self.media.mediaStatusChanged.connect(self.mediaStatusChanged)

        QShortcut(QKeySequence("Ctrl+Q"), self).activated \
            .connect(sys.exit)
        QShortcut(QKeySequence("Space"), self).activated \
            .connect(self.playPause)
        QShortcut(QKeySequence("Ctrl+F"), self).activated \
            .connect(self.onCtrlF)
        QShortcut(QKeySequence("Ctrl+Shift+F"), self).activated \
            .connect(lambda: self.setMode(MainWindow.FULL_MODE))
        QShortcut(QKeySequence("Ctrl+M"), self).activated \
            .connect(lambda: self.setMode(MainWindow.MINI_MODE))
        QShortcut(QKeySequence("Ctrl+Shift+M"), self).activated \
            .connect(lambda: self.setMode(MainWindow.MICRO_MODE))
        QShortcut(QKeySequence("F5"), self).activated \
            .connect(lambda: self.repopulateMedias())

        # populate media
        medias = Database.load(MainWindow.MEDIAS_FILE)
        if medias:
            self.medias = medias
            self.mediasAdded.emit(medias)
            if self.settings["fileWatch"]:
                for media in self.medias:
                    self.fsWatcher.addPath(pathUp(media.path))
                    self.fsWatcher.addPath(media.path)
        else:
            self.populateMediaThread()

    def setMode(self, mode):
        if mode == self.mode: return
        if mode == MainWindow.FULL_MODE:
            self.resize(QSize(1200, 900))
            centralWidget = MediaPlayer(self)
        elif mode == MainWindow.MINI_MODE:
            self.setMinimumSize(QSize(300, 475))
            self.resize(QSize(300, 475))
            centralWidget = PlayerWidget(self, PlayerWidget.MAIN_MODE)
        elif mode == MainWindow.MICRO_MODE:
            self.setMinimumSize(QSize(300, 65))
            self.resize(QSize(300, 65))
            centralWidget = PlayerWidget(self, PlayerWidget.MICRO_MODE)
        self.mode = mode
        self.setCentralWidget(centralWidget)
        # reemit events to redraw ui
        def emitAll():
            self.albumPath = ""
            if self.album: self.albumChanged.emit(self.album)
            if self.mediaInfo: self.songInfoChanged.emit(self.mediaInfo)
            self.media.durationChanged.emit(self.media.duration())
            self.media.positionChanged.emit(self.media.position())
        QTimer.singleShot(0, emitAll)

    # playback
    def playPause(self):
        if self.media.state() == QMediaPlayer.PlayingState:
            self.media.pause()
        else:
            self.media.play()

    # song info
    songInfoChanged = pyqtSignal(MediaInfo)

    def setSong(self, path):
        path = urllib.parse.unquote(path.strip())
        mediaContent = QMediaContent(QUrl.fromLocalFile(path))
        self.media.setMedia(mediaContent)
        self.media.play()
        self.setSongInfo(path)
        self.media.stateChanged.emit(self.media.state())

    def setSongInfo(self, path):
        self.mediaInfo = MediaInfo.fromFile(path)
        self.songInfoChanged.emit(self.mediaInfo)

    # dnd
    def dragEnterEvent(self, e):
        if e.mimeData().hasFormat("text/uri-list"):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        text = e.mimeData().text()
        if text.startswith("file://"):
            self.setSong(text[7:])

    # album
    albumChanged = pyqtSignal(list)
    def populateAlbum(self, path):
        if self.albumPath == path: return
        self.album.clear()
        search_path = pathUp(path)
        for f in os.listdir(search_path):
            fpath = os.path.join(search_path, f)
            if os.path.isfile(fpath) and getFileType(fpath) == "audio":
                mediaInfo = MediaInfo.fromFile(fpath)
                self.album.append(mediaInfo)
        self.album.sort()
        self.albumChanged.emit(self.album)
        self.albumPath = path

    def mediaStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia:
            self.nextSong()

    # controls
    def songIndex(self, array):
        try:
            i, _ = next(filter(lambda i: i[1] == self.mediaInfo, enumerate(array)))
            return i
        except StopIteration:
            return -1

    def nextSong(self):
        if self.mode == MainWindow.FULL_MODE and self.centralWidget().mode != MediaPlayer.PLAYING_ALBUM_MODE:
            self.nextSongArray(self.medias, 1)
        elif self.album:
            self.nextSongArray(self.album, 1)
    def prevSong(self):
        if self.mode == MainWindow.FULL_MODE and self.centralWidget().mode != MediaPlayer.PLAYING_ALBUM_MODE:
            self.nextSongArray(self.medias, -1)
        elif self.album:
            self.nextSongArray(self.album, -1)

    def nextSongArray(self, array, delta):
        idx = self.songIndex(array)
        if idx == -1: return
        if 0 <= idx+delta < len(array):
            self.setSong(array[idx+delta].path)

    # files
    mediasAdded = pyqtSignal(list)
    mediasDeleted = pyqtSignal(list)
    def populateMedias(self, path):
        batch = []
        ls = list(map(lambda f: os.path.join(path, f), os.listdir(path)))
        if not ls: return
        if self.settings["fileWatch"]:
            self.fsWatcher.addPath(path)
            self.fsWatcher.addPaths(ls)
        for fpath in ls:
            if os.path.isdir(fpath):
                self.populateMedias(fpath)
            elif os.access(fpath, os.R_OK) and getFileType(fpath) == "audio":
                try:
                    mediaInfo = MediaInfo.fromFile(fpath)
                    batch.append(mediaInfo)
                except OSError:
                    pass
        self.medias.extend(batch)
        self.mediasAdded.emit(batch)

    def populateMediaThread(self):
        class ProcessMediaThread(QThread):

            def run(self_):
                self.populateMedias(self.settings["mediaLocation"])
                Database.save(self.medias, MainWindow.MEDIAS_FILE)
                del self._thread

        self._thread = ProcessMediaThread()
        self._thread.start()

    def repopulateMedias(self):
        deleted = self.medias
        self.medias = []
        self.mediasDeleted.emit(deleted)
        self.setWatchFiles()
        QTimer.singleShot(0, self.populateMediaThread)

    # file watcher
    def setWatchFiles(self):
        if self.settings["fileWatch"]:
            self.fsWatcher = QFileSystemWatcher()
            if self.medias:
                for media in self.medias:
                    self.fsWatcher.addPath(pathUp(media.path))
                    self.fsWatcher.addPath(media.path)
            self.fsWatcher.fileChanged.connect(self.watchFileChanged)
            self.fsWatcher.directoryChanged.connect(self.watchDirChanged)
        elif hasattr(self, "fsWatcher"):
            del self.fsWatcher

    def watchFileChanged(self, fpath):
        try:
            i, mediaInfo = next(filter(lambda i: i[1].path == fpath, enumerate(self.medias)))
            self.mediasDeleted.emit([mediaInfo])
            del self.medias[i]
        except StopIteration:
            pass
        try:
            mediaInfo = MediaInfo.fromFile(fpath)
            self.medias.append(mediaInfo)
            self.mediasAdded.emit([mediaInfo])
        except OSError:
            return

    def watchDirChanged(self, dpath):
        print(dpath)
        # TODO: handle directories
        oldPaths = set(filter(lambda fpath: pathUp(fpath) == dpath,
            map(lambda info: info.path, self.medias)))
        newPaths = set(map(lambda fpath: os.path.join(dpath, fpath),
                filter(lambda fpath: getFileType(fpath) == "audio", os.listdir(dpath))))
        removed = oldPaths.difference(newPaths)
        added = newPaths.difference(oldPaths)

        for fpath in removed:
            i, mediaInfo = next(filter(lambda i: i[1].path == fpath, enumerate(self.medias)))
            self.mediasDeleted.emit([mediaInfo])
            del self.medias[i]
        for fpath in added:
            mediaInfo = MediaInfo.fromFile(fpath)
            self.medias.append(mediaInfo)
            self.mediasAdded.emit([mediaInfo])

    # settings
    def saveSettings(self):
        Database.save(self.settings, MainWindow.SETINGS_FILE, True)

    # misc
    def onCtrlF(self):
        self.setMode(MainWindow.FULL_MODE)
        self.centralWidget().fileListView.searchView.toggleVisible()

instance = None
