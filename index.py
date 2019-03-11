from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
import taglib
import sys
import os
import urllib.parse

class MediaInfo(object):

    def __init__(self, path, title, artist, image=None):
        self.path = path
        self.title = title
        self.artist = artist
        self.image = image
    
    def fromFile(path):
        song = taglib.File(path)
        artist = "unknown"
        if "ALBUMARTIST" in song.tags:
            artist = song.tags["ALBUMARTIST"][0]
        elif "ARTIST" in song.tags:
            artist = song.tags["ARTIST"][0]
        title = song.tags["TITLE"][0] if "TITLE" in song.tags else path
        searchPath = os.path.normpath(os.path.join(path, ".."))
        # find cover art
        paths = list(filter(lambda path: \
                        path.endswith(".jpg") or \
                        path.endswith(".jpeg") or \
                        path.endswith(".png"), os.listdir(searchPath)))
        if paths:
            prioritize = ["Cover.", "cover.", "CD."]
            def find_path():
                for path in paths:
                    for priority in prioritize:
                        if path.startswith(priority):
                            return path
                return paths[0]
            imagePath = find_path()
        else:
            imagePath = None
        return MediaInfo(path, title, artist,
                         os.path.join(searchPath, imagePath) if imagePath else None)

# base player widget
class PlayerWidget(QWidget):

    # modes
    MAIN_MODE   = 0
    MICRO_MODE  = 1
    WIDGET_MODE = 2

    def __init__(self, parent=None, mode=MAIN_MODE):
        QWidget.__init__(self, parent)

        # media player
        self.media = QMediaPlayer()
        self.mediaInfo = None
        self.mode = mode
        self.setAcceptDrops(True)

        # ui elements
        self.setStyleSheet("""
QSlider::groove:horizontal {
    height: 6px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
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
        self.stateChanged(self.media.state())
        if hasattr(self, "volumeButton"): self.mutedChanged(self.media.isMuted())
        self.bindEvents()

        # song
        self.updateInfo("no title", "no name", "")

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

        self.albumLabel = albumLabel = QLabel()
        albumLabel.setAlignment(Qt.AlignCenter)

        if self.mode == PlayerWidget.MAIN_MODE:
            self.artistLabel = artistLabel = QLabel()
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

        if self.mode != PlayerWidget.WIDGET_MODE:
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
            volumeSlider.setMaximum(200)
            volumeSlider.setValue(100)
            buttonsLayout.addWidget(volumeSlider)

            vboxLayout.addStretch()

    def setMode(self, mode):
        self.mode = mode
        self.initUI()

    def bindEvents(self):
        # song info
        ## pos slider
        self.media.durationChanged.connect(self.durationChanged)
        self.media.positionChanged.connect(self.positionChanged)
        self.positionSlider.valueChanged.connect(self.positionSliderChanged)

        # controls button
        self.backButton.clicked.connect(self.backButtonClicked)
        self.ppButton.clicked.connect(self.ppButtonClicked)
        self.media.stateChanged.connect(self.stateChanged)
        self.forwardButton.clicked.connect(self.forwardButtonClicked)
        if hasattr(self, "volumeButton"):
            self.volumeButton.clicked.connect(self.volumeButtonClicked)
            self.media.mutedChanged.connect(self.mutedChanged)
        if hasattr(self, "volumeSlider"):
            self.volumeSlider.valueChanged.connect(self.volumeSliderChanged)
            
        # misc
        self.media.error.connect(self.mediaError)

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
        self.media.setPosition(position)

    ## controls
    def backButtonClicked(self):
        raise NotImplementedError

    def ppButtonClicked(self):
        if self.media.state() == QMediaPlayer.PlayingState:
            self.media.pause()
        else:
            self.media.play()
    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.ppButton.setIcon(QIcon.fromTheme("media-playback-pause"))
        else:
            self.ppButton.setIcon(QIcon.fromTheme("media-playback-start"))

    def forwardButtonClicked(self):
        raise NotImplementedError

    ## volume mute
    def mutedChanged(self, muted):
        if muted:
            self.volumeButton.setIcon(QIcon.fromTheme("audio-volume-muted"))
        else:
            self.volumeButton.setIcon(QIcon.fromTheme("audio-volume-high"))

    def volumeButtonClicked(self):
        self.media.setMuted(not self.media.isMuted())

    ## volume slider
    def volumeSliderChanged(self, volume):
        self.media.setVolume(volume)

    # ui elements
    def updateInfo(self, title, artist, imagePath):
        if hasattr(self, "artistLabel"):
            self.albumLabel.setText(title)
            self.artistLabel.setText(artist)
        else:
            self.albumLabel.setText(title + " − " + artist)
        if hasattr(self, "coverLabel"):
            self.coverLabel.setPixmap(QPixmap.fromImage(QImage(imagePath)).scaledToWidth(300, Qt.SmoothTransformation))

    # song info
    songInfoChanged = pyqtSignal(MediaInfo)

    def setSong(self, path):
        path = urllib.parse.unquote(path.strip())
        mediaContent = QMediaContent(QUrl.fromLocalFile(path))
        self.media.setMedia(mediaContent)
        self.media.play()
        self.setSongInfo(path)
        self.stateChanged(self.media.state())

    def setSongInfo(self, path):
        self.mediaInfo = MediaInfo.fromFile(path)
        self.updateInfo(self.mediaInfo.title, self.mediaInfo.artist, self.mediaInfo.image)
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

# media label
class MediaLabel(QLabel):

    def __init__(self, media, parent):
        QLabel.__init__(self, parent)
        
        self.media = media
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
""" % (media.title, "00:00", media.artist))
    
    def mousePressEvent(self, e):
        print("press")

# album view
class PlayingAlbumView(QWidget):
    
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        
        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)
        
        self.albumLabel = albumLabel = QLabel("test")
        albumLabel.setAlignment(Qt.AlignCenter)
        albumLabel.setStyleSheet("font-size: 24px;")
        vboxLayout.addWidget(albumLabel)

        self.albumArtistLabel = albumArtistLabel = QLabel("test")
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
        mediaBox = QWidget()
        mediaBox.setStyleSheet(
"""
QLabel{
padding: 5px    ;
}
QLabel:hover {
background: red;
}
""")
        mediaBox.setObjectName("mediaBox")
        mediaBoxL = QVBoxLayout()
        mediaBox.setLayout(mediaBoxL)
        hboxLayout.addWidget(mediaBox)

        for media in [MediaInfo("", "Lorem ipsum blah blah", "blah blah"),
                      MediaInfo("", "blah blah blah blah", "blah blahblah blah"),
                      MediaInfo("", "blah blah blah blah", "blah blahblah blah"),
                      MediaInfo("", "blah blah blah blah", "blah blahblah blah"),
                      MediaInfo("", "blah blah blah blah", "blah blahblah blah")]:
            mediaBoxL.addWidget(MediaLabel(media, self))
            
        mediaBoxL.addStretch(1)
    
    def songInfoChanged(self, mediaInfo):
        if mediaInfo.image:
            self.coverLabel.setPixmap(QPixmap.fromImage(QImage(mediaInfo.image)).scaledToWidth(self.coverLabel.width(), Qt.SmoothTransformation))
            self.coverLabel.show()
        #TODO:
        self.albumLabel.setText(mediaInfo.title)
        self.albumArtistLabel.setText(mediaInfo.artist)

# application widget
class MediaPlayer(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setAcceptDrops(True)

        # ui
        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        vboxLayout.addStretch(1)
        self.view = PlayingAlbumView()
        vboxLayout.addWidget(self.view)

        #
        vboxLayout.addStretch(1)

        self.playerWidget = PlayerWidget(self, PlayerWidget.WIDGET_MODE)
        self.playerWidget.songInfoChanged.connect(self.view.songInfoChanged)
        vboxLayout.addWidget(self.playerWidget)

    # files
    def populateMedias(self, path):
        self.medias = []
        for f in os.listdir(path):
            if os.path.isdir(f):
                populateMedias(f)
            else:
                # TODO add files
                pass

    # dnd
    def dragEnterEvent(self, e):
        self.playerWidget.dragEnterEvent(e)

    def dropEvent(self, e):
        self.playerWidget.dropEvent(e)

class MainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        #full version
        self.resize(QSize(1200, 900))

        # mini version
        #self.setMinimumSize(QSize(300, 475))

        # micro version
        #self.setMinimumSize(QSize(300, 45))
        #self.setMaximumSize(QSize(300, 45))

        self.setWindowTitle("Hello world")
        self.setStyleSheet("background: #fff; color: #000;")

        #self.centralWidget = PlayerWidget(self, PlayerWidget.MAIN_MODE)
        self.centralWidget = MediaPlayer(self)
        self.setCentralWidget(self.centralWidget)

app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
