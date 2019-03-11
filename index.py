from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
import taglib
import sys
import os
import urllib.parse
import datetime
from functools import total_ordering

def path_up(path):
    return os.path.normpath(os.path.join(path, ".."))

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

@total_ordering
class MediaInfo(object):

    def __init__(self, path, pos, title, artist, duration, image):
        self.path = path
        self.pos = pos
        self.title = title
        self.artist = artist
        self.duration = duration
        self.image = image

    def fromFile(path):
        song = taglib.File(path)
        artist = "unknown"
        if "ALBUMARTIST" in song.tags:
            artist = song.tags["ALBUMARTIST"][0]
        elif "ARTIST" in song.tags:
            artist = song.tags["ARTIST"][0]
        title = song.tags["TITLE"][0] if "TITLE" in song.tags else path
        searchPath = path_up(path)
        # find cover art
        paths = list(filter(lambda path: \
                        path.endswith(".jpg") or \
                        path.endswith(".jpeg") or \
                        path.endswith(".png") or \
                        path.endswith(".bmp"), os.listdir(searchPath)))
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
        pos = int(song.tags["TRACKNUMBER"][0]) if song.tags["TRACKNUMBER"] else -1
        return MediaInfo(path, pos, title, artist, datetime.datetime.fromtimestamp(song.length),
                         os.path.join(searchPath, imagePath) if imagePath else None)

    # comparators
    def __lt__(self, other):
        if self.pos != -1 and other.pos != -1:
            return self.pos < other.pos
        return self.title < other.title

    def __eq__(self, other):
        if os.path.samefile(self.path, other.path):
            return True
        return object.__eq__(self, other)

# base player widget
class PlayerWidget(QWidget):

    # modes
    MAIN_MODE   = 0
    MICRO_MODE  = 1
    WIDGET_MODE = 2

    def __init__(self, parent=None, mode=MAIN_MODE):
        QWidget.__init__(self, parent)

        # media player
        self.mode = mode
        self.setAcceptDrops(True)

        # ui elements
        self.setStyleSheet("""
QSlider::groove:horizontal {
    height: 6px;
    background: rgba(0, 0, 0, 0.2);
    margin: 0 0;
}
QSlider::sub-page:horizontal {
    background: #9fabb3;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: #778791;
    width: 6px;
}
""")
        self.initUI()

        # events
        self.stateChanged(MainWindow.getInstance().media.state())
        if hasattr(self, "volumeButton"): self.mutedChanged(MainWindow.getInstance().media.isMuted())
        self.bindEvents()

    def initUI(self):
        vboxLayout = QVBoxLayout(self)
        vboxLayout.setContentsMargins(0, 0, 0, 0)
        vboxLayout.setSpacing(0)
        self.setLayout(vboxLayout)

        # song info
        self.positionSlider = slider = QSlider(Qt.Horizontal)
        slider.setTracking(True)
        if self.mode != PlayerWidget.WIDGET_MODE:
            slider.setStyleSheet("margin-top:-6px;")

        self.albumLabel = albumLabel = QLabel("no title")
        albumLabel.setAlignment(Qt.AlignCenter)

        if self.mode == PlayerWidget.MAIN_MODE:
            self.artistLabel = artistLabel = QLabel("no name")
            artistLabel.setAlignment(Qt.AlignCenter)

        if self.mode == PlayerWidget.MICRO_MODE:
            vboxLayout.addWidget(slider)
        elif self.mode == PlayerWidget.MAIN_MODE:
            coverLabelContainer = QWidget(self)
            coverLabelContainer.setStyleSheet("background: #000;")
            coverLabelContainerL = QHBoxLayout(self)
            coverLabelContainerL.setSpacing(0)
            coverLabelContainerL.setContentsMargins(0, 0, 0, 0)
            coverLabelContainer.setLayout(coverLabelContainerL)

            self.coverLabel = coverLabel = QLabel(coverLabelContainer)
            coverLabel.setAlignment(Qt.AlignCenter)
            coverLabel.setMinimumSize(QSize(300, 300))
            coverLabel.setMaximumSize(QSize(300, 300))
            coverLabelContainerL.addWidget(coverLabel)
            vboxLayout.addWidget(coverLabelContainer)

            vboxLayout.addWidget(slider)
            vboxLayout.addStretch()
            vboxLayout.addWidget(albumLabel)
            albumLabel.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
            vboxLayout.addWidget(artistLabel)
            artistLabel.setStyleSheet("font-size: 12px; margin-bottom: 15px;")

        # buttons
        buttonsWidget = QWidget()
        buttonsWidget.setStyleSheet("""
QPushButton {
    width: 24px;
    height: 24px;
    qproperty-iconSize: 24px;
    border: 0 none;
}
""")

        buttonsLayout = QHBoxLayout(self)
        buttonsWidget.setLayout(buttonsLayout)

        self.backButton = backButton = QPushButton(QIcon.fromTheme("media-skip-backward"), "")

        self.ppButton = ppButton = QPushButton()

        self.forwardButton = forwardButton = QPushButton(QIcon.fromTheme("media-skip-forward"), "")

        if self.mode == PlayerWidget.MICRO_MODE:
            vboxLayout.addWidget(buttonsWidget)
            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)
            buttonsLayout.addStretch()
            buttonsLayout.addWidget(albumLabel)
            albumLabel.setStyleSheet("font-size: 12px;")
            buttonsLayout.addStretch()
        elif self.mode == PlayerWidget.MAIN_MODE:
            vboxLayout.addWidget(buttonsWidget)
            buttonsLayout.addStretch()
            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)
            buttonsLayout.addStretch()

        if self.mode == PlayerWidget.MAIN_MODE:
            vboxLayout.addStretch()

        # widget mode - separated because it's fundamentally different
        if self.mode == PlayerWidget.WIDGET_MODE:
            vboxLayout.addStretch()

            vboxLayout.addWidget(albumLabel)
            vboxLayout.addWidget(buttonsWidget)

            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)

            buttonsLayout.addWidget(slider)

            self.volumeButton = volumeButton = QPushButton()
            buttonsLayout.addWidget(volumeButton)
            self.volumeSlider = volumeSlider = QSlider(Qt.Horizontal)
            volumeSlider.setStyleSheet("max-width: 100%;")
            volumeSlider.setMinimum(0)
            volumeSlider.setMaximum(100)
            volumeSlider.setValue(100)
            buttonsLayout.addWidget(volumeSlider)

            vboxLayout.addStretch()

    def setMode(self, mode):
        self.mode = mode
        self.initUI()

    def bindEvents(self):
        media = MainWindow.getInstance().media

        # song info
        MainWindow.getInstance().songInfoChanged.connect(self.updateInfo)
        ## pos slider
        media.durationChanged.connect(self.durationChanged)
        media.positionChanged.connect(self.positionChanged)
        self.positionSlider.valueChanged.connect(self.positionSliderChanged)

        # controls button
        self.backButton.clicked.connect(self.backButtonClicked)
        self.ppButton.clicked.connect(self.ppButtonClicked)
        media.stateChanged.connect(self.stateChanged)
        self.forwardButton.clicked.connect(self.forwardButtonClicked)
        if hasattr(self, "volumeButton"):
            self.volumeButton.clicked.connect(self.volumeButtonClicked)
            media.mutedChanged.connect(self.mutedChanged)
        if hasattr(self, "volumeSlider"):
            self.volumeSlider.valueChanged.connect(self.volumeSliderChanged)

        # misc
        media.error.connect(self.mediaError)

    # events
    # media
    def mediaError(self, e):
        print("error", e)

    ## position slider
    def durationChanged(self, duration):
        self.positionSlider.setMaximum(duration)

    def positionChanged(self, position):
        self.positionSlider.blockSignals(True)
        self.positionSlider.setValue(position)
        self.positionSlider.blockSignals(False)

    def positionSliderChanged(self, position):
        MainWindow.getInstance().media.setPosition(position)

    ## controls
    def backButtonClicked(self):
        MainWindow.getInstance().albumPrev()

    def forwardButtonClicked(self):
        MainWindow.getInstance().albumNext()

    def ppButtonClicked(self):
        media = MainWindow.getInstance().media
        if media.state() == QMediaPlayer.PlayingState:
            media.pause()
        else:
            media.play()
    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.ppButton.setIcon(QIcon.fromTheme("media-playback-pause"))
        else:
            self.ppButton.setIcon(QIcon.fromTheme("media-playback-start"))

    ## volume mute
    def mutedChanged(self, muted):
        if muted:
            self.volumeButton.setIcon(QIcon.fromTheme("audio-volume-muted"))
        else:
            self.volumeButton.setIcon(QIcon.fromTheme("audio-volume-high"))

    def volumeButtonClicked(self):
        media = MainWindow.getInstance().media
        media.setMuted(not media.isMuted())

    ## volume slider
    def volumeSliderChanged(self, volume):
        MainWindow.getInstance().media.setVolume(volume)

    # ui elements
    def updateInfo(self, mediaInfo):
        if hasattr(self, "artistLabel"):
            self.albumLabel.setText(mediaInfo.title)
            self.artistLabel.setText(mediaInfo.artist)
        else:
            self.albumLabel.setText(mediaInfo.title + " − " + mediaInfo.artist)
        if hasattr(self, "coverLabel"):
            self.coverLabel.setPixmap(QPixmap.fromImage(QImage(mediaInfo.image)).scaledToWidth(300, Qt.SmoothTransformation))


# media label
class MediaLabel(QLabel):

    def __init__(self, media, parent):
        QLabel.__init__(self, parent)

        self.media = media
        self.initUI()

    # ui
    def initUI(self):
        self.setText(
"""
<table>
<tr>
    <td width='250'>%s</td>
    <td>%s</td>
</tr>
<tr>
    <td>%s</td>
</tr>
</table>
""" % (self.media.title, self.media.duration.strftime("%M:%S"), self.media.artist))

    # activity
    def setActive(self, active):
        if active:
            self.setProperty("class", "active")
        else:
            self.setProperty("class", "")

    # events
    def mousePressEvent(self, e):
        MainWindow.getInstance().setSong(self.media.path)

# album view
class PlayingAlbumView(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.initUI()
        self.bindEvents()

    def initUI(self):
        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        self.albumLabel = albumLabel = QLabel("no title")
        albumLabel.setAlignment(Qt.AlignCenter)
        albumLabel.setStyleSheet("font-size: 24px;")
        vboxLayout.addWidget(albumLabel)

        self.albumArtistLabel = albumArtistLabel = QLabel("no name")
        albumArtistLabel.setAlignment(Qt.AlignCenter)
        albumArtistLabel.setStyleSheet("font-size: 12px;")
        vboxLayout.addWidget(albumArtistLabel)

        #
        hbox = QWidget()
        vboxLayout.addWidget(hbox)
        vboxLayout.setAlignment(hbox,Qt.AlignCenter)
        hboxLayout = QHBoxLayout()
        hbox.setLayout(hboxLayout)

        self.coverLabel = coverLabel = QLabel()
        coverLabel.setMinimumSize(QSize(400, 400))
        coverLabel.setMaximumSize(QSize(400, 400))
        coverLabel.hide()
        hboxLayout.addWidget(coverLabel)

        # media box
        self.scrollArea = scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setMinimumSize(QSize(320, 300))
        scrollArea.hide()
        scrollArea.setStyleSheet("""
QScrollArea{
border:0 none;
margin-right: 5px;
}
QScrollBar::handle {
    background: #9fabb3;
}
""")
        hboxLayout.addWidget(scrollArea)

        mediaBox = QWidget()
        scrollArea.setWidget(mediaBox)
        mediaBox.setStyleSheet(
"""
QLabel{
padding: 5px;
}
QLabel:hover, QLabel.active {
background: #9fabb3;
color: #fff;
}
""")
        self.mediaBoxL = mediaBoxL = QVBoxLayout()
        mediaBox.setLayout(mediaBoxL)
        mediaBoxL.addStretch(1)
        self.mediaLabels = []

    def bindEvents(self):
        MainWindow.getInstance().albumChanged.connect(self.populateAlbum)

    def songInfoChanged(self, mediaInfo):
        # song info
        if mediaInfo.image:
            self.coverLabel.setPixmap(QPixmap.fromImage(QImage(mediaInfo.image)).scaledToWidth(self.coverLabel.width(), Qt.SmoothTransformation))
            self.coverLabel.show()
        self.albumLabel.setText(mediaInfo.title)
        self.albumArtistLabel.setText(mediaInfo.artist)

        # album
        mainWindow = MainWindow.getInstance()
        mainWindow.populateAlbum(mediaInfo.path)
        for mediaLabel in self.mediaLabels:
            mediaLabel.setActive(mediaLabel.media == mediaInfo)


    def populateAlbum(self, path):
        self.scrollArea.show()
        self.mediaLabels.clear()
        clearLayout(self.mediaBoxL)
        for mediaInfo in MainWindow.getInstance().album:
            mediaLabel = MediaLabel(mediaInfo, self)
            self.mediaBoxL.addWidget(mediaLabel)
            self.mediaLabels.append(mediaLabel)
        self.mediaBoxL.addStretch(1)


# application widget
class MediaPlayer(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        # ui
        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        vboxLayout.addStretch(1)
        self.view = PlayingAlbumView()
        vboxLayout.addWidget(self.view)

        #
        vboxLayout.addStretch(1)

        self.playerWidget = PlayerWidget(self, PlayerWidget.WIDGET_MODE)
        vboxLayout.addWidget(self.playerWidget)

        MainWindow.getInstance().songInfoChanged.connect(self.view.songInfoChanged)

    # files
    def populateMedias(self, path):
        self.medias = []
        for f in os.listdir(path):
            if os.path.isdir(f):
                populateMedias(f)
            else:
                # TODO add files
                pass

class MainWindow(QMainWindow):

    # modes
    FULL_MODE = 0
    MINI_MODE = 1
    MICRO_MODE = 2

    # instance
    _instance = None
    def getInstance():
        return MainWindow._instance

    # main
    def __init__(self):
        MainWindow._instance = self
        QMainWindow.__init__(self)
        self.setAcceptDrops(True)

        self.media = QMediaPlayer()
        self.mediaInfo = None
        self.album = []
        self.albumPath = ""

        self.setWindowTitle("Hello world")
        self.setStyleSheet("background: #fff; color: #000;")
        self.setMode(MainWindow.FULL_MODE)

        self.media.mediaStatusChanged.connect(self.mediaStatusChanged)

        QShortcut(QKeySequence("Ctrl+Shift+F"), self).activated \
            .connect(lambda: self.setMode(MainWindow.FULL_MODE))
        QShortcut(QKeySequence("Ctrl+M"), self).activated \
            .connect(lambda: self.setMode(MainWindow.MINI_MODE))
        QShortcut(QKeySequence("Ctrl+Shift+M"), self).activated \
            .connect(lambda: self.setMode(MainWindow.MICRO_MODE))

    def setMode(self, mode):
        if mode == MainWindow.FULL_MODE:
            self.resize(QSize(1200, 900))
            self.centralWidget = MediaPlayer(self)
        elif mode == MainWindow.MINI_MODE:
            self.setMinimumSize(QSize(300, 475))
            self.resize(QSize(300, 475))
            self.centralWidget = PlayerWidget(self, PlayerWidget.MAIN_MODE)
        elif mode == MainWindow.MICRO_MODE:
            self.setMinimumSize(QSize(300, 65))
            self.resize(QSize(300, 65))
            self.centralWidget = PlayerWidget(self, PlayerWidget.MICRO_MODE)
        self.setCentralWidget(self.centralWidget)
        # reemit events to redraw ui
        self.albumPath = ""
        if self.album: self.albumChanged.emit(self.album)
        if self.mediaInfo: self.songInfoChanged.emit(self.mediaInfo)
        self.media.durationChanged.emit(self.media.duration())
        self.media.positionChanged.emit(self.media.position())

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
        search_path = path_up(path)
        self.album.clear()
        for f in os.listdir(search_path):
            fpath = os.path.join(search_path, f)
            if  os.path.isfile(fpath) and \
                (f.endswith(".mp3") or f.endswith(".flac") or f.endswith(".m4a")): # TODO
                mediaInfo = MediaInfo.fromFile(fpath)
                self.album.append(mediaInfo)
        self.album.sort()
        self.albumChanged.emit(self.album)
        self.albumPath = path

    def mediaStatusChanged(self, status):
        if status == QMediaPlayer.EndOfMedia and self.album:
            self.albumNext()

    def songIndexAlbum(self):
        for i, info in enumerate(self.album):
            if info == self.mediaInfo:
                return i
        return -1

    def albumNext(self):
        idx = self.songIndexAlbum() + 1
        if 0 <= idx < len(self.album):
            self.setSong(self.album[idx].path)

    def albumPrev(self):
        idx = self.songIndexAlbum() - 1
        if 0 <= idx < len(self.album):
            self.setSong(self.album[idx].path)

app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
