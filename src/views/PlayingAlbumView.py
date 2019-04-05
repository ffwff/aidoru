from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .PlayerWidget import PlayerWidget
from .MediaLabel import MediaLabel
from src.utils import clearLayout, pathUp, dropShadow
from src.Application import Application

class PlayingAlbumView(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.initUI()
        self.bindEvents()

    def initUI(self):
        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        vboxLayout.addStretch(1)

        self.albumLabel = albumLabel = QLabel("no title")
        albumLabel.setAlignment(Qt.AlignCenter)
        albumLabel.setProperty("class", "album-label")
        vboxLayout.addWidget(albumLabel)

        self.albumArtistLabel = albumArtistLabel = QLabel("no name")
        albumArtistLabel.setAlignment(Qt.AlignCenter)
        albumLabel.setProperty("class", "artist-label")
        vboxLayout.addWidget(albumArtistLabel)

        #
        hbox = QWidget()
        vboxLayout.addWidget(hbox)
        vboxLayout.setAlignment(hbox,Qt.AlignCenter)
        hboxLayout = QHBoxLayout()
        hbox.setLayout(hboxLayout)

        self.coverLabel = coverLabel = QLabel()
        coverLabel.setGraphicsEffect(dropShadow())
        size = QSize(400 + coverLabel.graphicsEffect().blurRadius()*2,
                     400 + coverLabel.graphicsEffect().blurRadius()*2)
        coverLabel.setMinimumSize(size)
        coverLabel.setMaximumSize(size)
        coverLabel.hide()
        hboxLayout.addWidget(coverLabel,Qt.AlignTop)

        # media box
        self.scrollArea = scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setMinimumSize(QSize(310, 300))
        scrollArea.hide()
        hboxLayout.addWidget(scrollArea,Qt.AlignTop)

        mediaBox = QWidget()
        mediaBox.setProperty("class", "media-box")
        scrollArea.setWidget(mediaBox)
        self.mediaBoxL = mediaBoxL = QVBoxLayout()
        mediaBox.setLayout(mediaBoxL)
        mediaBoxL.addStretch(1)
        self.mediaLabels = []

        vboxLayout.addStretch(1)

    def bindEvents(self):
        mainWindow = Application.mainWindow
        mainWindow.albumChanged.connect(self.populateAlbum)
        mainWindow.songInfoChanged.connect(self.songInfoChanged)

    def songInfoChanged(self, mediaInfo):
        # song info
        if mediaInfo.image:
            self.coverLabel.setPixmap(QPixmap(mediaInfo.image).scaledToWidth(400, Qt.SmoothTransformation))
            self.coverLabel.show()
        else:
            self.coverLabel.hide()
        self.albumLabel.setText(mediaInfo.album)
        self.albumArtistLabel.setText(mediaInfo.albumArtist)

        # album
        Application.mainWindow.populateAlbum(mediaInfo)
        for mediaLabel in self.mediaLabels:
            mediaLabel.setActive(mediaLabel.media == mediaInfo)

    def populateAlbum(self, album):
        self.scrollArea.show()
        self.mediaLabels.clear()
        clearLayout(self.mediaBoxL)
        for mediaInfo in album.medias:
            mediaLabel = MediaLabel(mediaInfo, self)
            self.mediaBoxL.addWidget(mediaLabel)
            self.mediaLabels.append(mediaLabel)
        self.mediaBoxL.addStretch(1)
