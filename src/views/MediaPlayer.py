from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from sys import exit
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
        self.mpos = None
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
        self.background = QGraphicsScene(self)
        self.background.setBackgroundBrush(Qt.black)
        self.backgroundLabel = QGraphicsView(self.background, self)
        self.backgroundItem = QGraphicsPixmapItem()
        self.backgroundItem.setOpacity(0.6)
        self.background.addItem(self.backgroundItem)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(90)
        self.backgroundItem.setGraphicsEffect(blur)

        def resizeBg():
            self.backgroundLabel.setGeometry(self.geometry())
            self.backgroundLabel.fitInView(self.backgroundItem, Qt.IgnoreAspectRatio)
        QTimer.singleShot(0, resizeBg)

        self.layout = layout = QGridLayout()
        self.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.setColumnStretch(1, 1)

        self.playerWidget = PlayerWidget(self, PlayerWidget.WIDGET_MODE)
        layout.addWidget(self.playerWidget, 1, 1, 1, 1)

        self.menu = MediaPlayerMenu(self)
        layout.addWidget(self.menu, 0, 0, 2, 1)

        self.fileListView = FileListView()
        self.playingAlbumView = PlayingAlbumView()
        self.settingsView = SettingsView()

        self.mode = MediaPlayer.FILE_LIST_MODE
        self.view = self.fileListView
        layout.addWidget(self.view, 0, 1)

        self.windowDecorations = QWidget(self)
        self.windowDecorations.setObjectName("window-decorations")
        self.windowDecorations.resize(QSize(0, 24))
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        self.windowDecorations.setLayout(layout)

        self.minimizeButton = QPushButton(QIcon("./icons/window-minimize.svg"), "")
        self.minimizeButton.clicked.connect(lambda: Application.mainWindow.setWindowState(Qt.WindowMinimized))
        layout.addWidget(self.minimizeButton)

        self.maximizeButton = QPushButton(QIcon("./icons/window-maximize.svg"), "")
        self.maximizeButton.clicked.connect(lambda: Application.mainWindow.setWindowState(Qt.WindowMaximized))
        layout.addWidget(self.maximizeButton)

        self.closeButton = QPushButton(QIcon("./icons/window-close.svg"), "")
        self.closeButton.clicked.connect(lambda: exit(0))
        layout.addWidget(self.closeButton)

        width = 0
        for i in range(layout.count()):
            child = layout.itemAt(i).widget()
            child.resize(QSize(24,24))
            width += child.width()
        self.windowDecorations.resize(QSize(width, 24))
        self.windowDecorations.raise_()

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

    def setBackgroundFromPath(self, path):
        self.backgroundItem.setPixmap(QPixmap(path).scaled(self.width(), self.height()))
        self.resizeBg()

    def bindEvents(self):
        from src.modules.disablewindowdecorations import DisableWindowDecorationsModule
        DisableWindowDecorationsModule.connect(self.windowDecorationsChanged)
        self.parent().songInfoChanged.connect(self.songInfoChanged)
    
    def songInfoChanged(self, info):
        self.setBackgroundFromPath(info.image)

    def windowDecorationsChanged(self, enabled):
        self.windowDecorations.setVisible(enabled)

    def resizeBg(self):
        self.backgroundLabel.setGeometry(self.geometry())
        self.backgroundLabel.fitInView(self.backgroundItem, Qt.IgnoreAspectRatio)

    def resizeEvent(self, event):
        self.windowDecorations.move(QPoint(
            self.size().width() - self.windowDecorations.width() - 4,
            5))
        self.resizeBg()
        # self.backgroundLabel.setPixmap(self.background.scaled(self.size()))

    def mousePressEvent(self, event):
        # HACK: qt doesn't allow redirect mouse events for buttons in "background" widgets
        for btn in self.windowDecorations.children():
            if isinstance(btn, QPushButton):
                x = self.windowDecorations.x() + btn.x()
                y = self.windowDecorations.y() + btn.y()
                if x <= event.x() <= x+btn.width() and \
                   y <= event.y() <= y+btn.height():
                    btn.click()
                    return
