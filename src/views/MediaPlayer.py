from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from .WindowDragger import WindowDragger
from .FileListView import FileListView
from .PlayingAlbumView import PlayingAlbumView
from .SettingsView import SettingsView
from .PlayerWidget import PlayerWidget
from src.Application import Application

class MediaPlayerMenu(WindowDragger, QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setObjectName("media-player-menu")
        self.initUI()
        self.bindEvents()

    def initUI(self):
        self.layout = vboxLayout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setLayout(vboxLayout)

        self.fileButton = QPushButton(QIcon("./icons/files"), "")
        vboxLayout.addWidget(self.fileButton)

        self.albumButton = QPushButton(QIcon("./icons/album"), "")
        vboxLayout.addWidget(self.albumButton)

        self.findButton = QPushButton(QIcon("./icons/find"), "")
        vboxLayout.addWidget(self.findButton)
        vboxLayout.addWidget(QWidget())

        self.settingsButton = QPushButton(QIcon("./icons/settings"), "")
        vboxLayout.addWidget(self.settingsButton)

    def bindEvents(self):
        self.fileButton.clicked.connect \
            (lambda: self.parentWidget().setMode(MediaPlayer.FILE_LIST_MODE))
        self.albumButton.clicked.connect \
            (lambda: self.parentWidget().setMode(MediaPlayer.PLAYING_ALBUM_MODE))
        self.findButton.clicked.connect \
            (lambda: self.parentWidget().fileListView.searchView.toggleVisible())
        self.settingsButton.clicked.connect \
            (lambda: self.parentWidget().setMode(MediaPlayer.SETTINGS_MODE))

# application widget
class MediaPlayer(QWidget):

    # modes
    FILE_LIST_MODE = 0
    PLAYING_ALBUM_MODE = 1
    SETTINGS_MODE = 2

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setObjectName("media-player")
        self.initUI()
        self.bindEvents()

    def initUI(self):
        self.layout = layout = QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.setColumnStretch(1, 1)

        self.menu = MediaPlayerMenu(self)
        layout.addWidget(self.menu, 0, 0)

        self.fileListView = FileListView()
        self.playingAlbumView = PlayingAlbumView()
        self.settingsView = SettingsView()

        self.mode = MediaPlayer.FILE_LIST_MODE
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
        elif mode == MediaPlayer.SETTINGS_MODE:
            view = self.settingsView
        self.layout.replaceWidget(self.view, view)
        self.view = view
        self.view.show()
        return True

    #events
    def bindEvents(self):
        pass
