from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .FileListView import FileListView
from .PlayingAlbumView import PlayingAlbumView
from .PlayerWidget import PlayerWidget

class MediaPlayerMenu(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setObjectName("media-player-menu")
        self.initUI()
        self.bindEvents()

    def initUI(self):
        self.layout = vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        self.fileButton = QPushButton(QIcon("./icons/files"), "")
        vboxLayout.addWidget(self.fileButton)

        self.albumButton = QPushButton(QIcon("./icons/album"), "")
        vboxLayout.addWidget(self.albumButton)

        self.findButton = QPushButton(QIcon("./icons/find"), "")
        vboxLayout.addWidget(self.findButton)

        vboxLayout.addStretch(1)

    def bindEvents(self):
        self.fileButton.clicked.connect \
            (lambda: self.parentWidget().setMode(MediaPlayer.FILE_LIST_MODE))
        self.albumButton.clicked.connect \
            (lambda: self.parentWidget().setMode(MediaPlayer.PLAYING_ALBUM_MODE))
        self.findButton.clicked.connect \
            (lambda: self.parentWidget().fileListView.searchView.toggleVisible())

# application widget
class MediaPlayer(QWidget):

    # modes
    FILE_LIST_MODE = 0
    PLAYING_ALBUM_MODE = 1

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.mode = MediaPlayer.FILE_LIST_MODE
        self.initUI()
        self.bindEvents()

    def initUI(self):
        self.layout = layout = QGridLayout()
        self.setLayout(layout)
        layout.setColumnStretch(1, 1)

        self.menu = MediaPlayerMenu(self)
        layout.addWidget(self.menu, 0, 0)

        self.fileListView = FileListView()
        self.playingAlbumView = PlayingAlbumView()
        self.view = self.fileListView
        layout.addWidget(self.view, 0, 1)

        self.playerWidget = PlayerWidget(self, PlayerWidget.WIDGET_MODE)
        layout.addWidget(self.playerWidget, 1, 0, 1, 2)

    def setMode(self, mode):
        if mode == self.mode: return False
        self.mode = mode
        self.view.hide()
        if mode == MediaPlayer.FILE_LIST_MODE:
            view = self.fileListView
        elif mode == MediaPlayer.PLAYING_ALBUM_MODE:
            view = self.playingAlbumView
        self.layout.replaceWidget(self.view, view)
        self.view = view
        self.view.show()
        return True

    #events
    def bindEvents(self):
        pass
