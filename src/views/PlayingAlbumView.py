from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import src.MainWindow as MainWindow
from .PlayerWidget import PlayerWidget
from .MediaLabel import MediaLabel
from src.utils import clearLayout

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
        scrollArea.setMinimumSize(QSize(310, 300))
        scrollArea.hide()
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

        vboxLayout.addStretch(1)

    def bindEvents(self):
        mainWindow = MainWindow.instance
        mainWindow.albumChanged.connect(self.populateAlbum)
        mainWindow.songInfoChanged.connect(self.songInfoChanged)

    def songInfoChanged(self, mediaInfo):
        # song info
        if mediaInfo.image:
            self.coverLabel.setPixmap(QPixmap.fromImage(QImage(mediaInfo.image)).scaledToWidth(self.coverLabel.width(), Qt.SmoothTransformation))
            self.coverLabel.show()
        else:
            self.coverLabel.hide()
        self.albumLabel.setText(mediaInfo.album)
        self.albumArtistLabel.setText(mediaInfo.albumArtist)

        # album
        mainWindow = MainWindow.instance
        mainWindow.populateAlbum(mediaInfo.path)
        for mediaLabel in self.mediaLabels:
            mediaLabel.setActive(mediaLabel.media == mediaInfo)

    def populateAlbum(self, path):
        self.scrollArea.show()
        self.mediaLabels.clear()
        clearLayout(self.mediaBoxL)
        for mediaInfo in MainWindow.instance.album:
            mediaLabel = MediaLabel(mediaInfo, self)
            self.mediaBoxL.addWidget(mediaLabel)
            self.mediaLabels.append(mediaLabel)
        self.mediaBoxL.addStretch(1)
