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
        self.coverPixmap = None
        self.coverRatio = 0
        coverLabel.setGraphicsEffect(dropShadow())
        coverLabel.hide()
        hboxLayout.addWidget(coverLabel,Qt.AlignRight)

        # media box
        self.scrollArea = scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setMinimumSize(QSize(310, 350))
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

    def resizeEvent(self, event):
        if not self.coverPixmap or self.coverLabel.height() == 0:
            return
        h = min(self.coverPixmap.height(), self.parentWidget().height()*0.5)
        w = self.coverRatio*h
        self.coverLabel.setPixmap(self.coverPixmap.scaledToHeight(h, Qt.SmoothTransformation))
        self.coverLabel.resize(w, h)
        self.coverLabel.move(QPoint(self.coverLabel.parentWidget().width()-self.scrollArea.width()-w-20, 0))

    def bindEvents(self):
        mainWindow = Application.mainWindow
        mainWindow.albumChanged.connect(self.populateAlbum)
        mainWindow.songInfoChanged.connect(self.songInfoChanged)

    def songInfoChanged(self, mediaInfo):
        # song info
        if mediaInfo.image:
            self.coverPixmap = pixmap = QPixmap(mediaInfo.image)
            self.coverLabel.setPixmap(pixmap)
            self.coverRatio = pixmap.width() / pixmap.height()
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
