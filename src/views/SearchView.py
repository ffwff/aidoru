from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.Application import Application
from src.utils import clearLayout, dropShadow, highlightText

class AlbumLabel(QWidget):

    def __init__(self, parent, album, highlight=None):
        QWidget.__init__(self, parent)
        self.album = album
        self.initUI(highlight)

    def initUI(self, highlight=None):
        size = QSize(165, 200)
        self.setMinimumSize(size)
        self.setMaximumSize(size)
        self.resize(size)

        width = 140

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.coverLabelContainer = coverLabelContainer = QWidget(self)
        coverLabelContainer.setObjectName("cover-label")
        coverLabelContainer.setMinimumSize(QSize(width+15, width+15))
        layout.addWidget(coverLabelContainer)

        coverLabelBg = QLabel(coverLabelContainer)

        self.coverLabel = coverLabel = QLabel(coverLabelContainer)
        if self.album.image:
            pixmap = QPixmap(self.album.image)
            if pixmap.width() == 0 or pixmap.height() == 0:
                pixmap = QIcon("./icons/album.svg").pixmap(QSize(width, width))
            elif pixmap.width() >= pixmap.height():
                pixmap = pixmap.scaledToWidth(width, Qt.SmoothTransformation)
            else:
                pixmap = pixmap.scaledToHeight(width, Qt.SmoothTransformation)
        else:
            pixmap = QIcon("./icons/album.svg").pixmap(QSize(width, width))
        coverLabel.setPixmap(pixmap)
        coverLabel.setGraphicsEffect(dropShadow())
        coverLabel.move(coverLabelContainer.width()//2 - pixmap.width()//2,
                        coverLabelContainer.height()//2 - pixmap.height()//2)

        if highlight != None:
          self.titleLabel = QLabel(highlightText(self.album.title, highlight), self)
        else:
          self.titleLabel = QLabel(self.album.title, self)
        self.titleLabel.setMaximumSize(QSize(self.width(), self.titleLabel.height()))
        layout.addWidget(self.titleLabel)

        self.artistLabel = QLabel(self.album.artist, self)
        self.artistLabel.setMaximumSize(QSize(self.width(), self.artistLabel.height()))
        self.artistLabel.setWordWrap(True)
        layout.addWidget(self.artistLabel)

    def mousePressEvent(self, event):
        Application.mainWindow.setSong(self.album.medias[0])

class SearchView(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.setObjectName("search-view")
        self.initUI()
        self.bindEvents()

    def initUI(self):
        clayout = QVBoxLayout()
        clayout.setContentsMargins(5,5,5,0)
        clayout.setSpacing(0)
        self.setLayout(clayout)
        container = QWidget()
        clayout.addWidget(container)

        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0,0,0,0)
        vlayout.setSpacing(0)
        container.setLayout(vlayout)

        layoutw = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layoutw.setLayout(layout)
        vlayout.addWidget(layoutw)

        self.searchBox = searchBox = QLineEdit()
        layout.addWidget(searchBox)

        self.openButton = QPushButton("Open")
        layout.addWidget(self.openButton)

        # HACK to pad the search bar
        self.navbarPadding = QWidget()
        layout.addWidget(self.navbarPadding)

        self.albumScroll = scrollArea = QScrollArea()
        scrollArea.hide()
        scrollArea.setMinimumSize(QSize(0, 200))
        scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        scrollArea.setWidgetResizable(True)
        scrollArea.installEventFilter(self)
        vlayout.addWidget(scrollArea)

        self.albumContainer = QWidget(scrollArea)
        scrollArea.setWidget(self.albumContainer)

        self.nchild = 0
        self.albumLabels = []

    # album add
    def addAlbumLabel(self, albumLabel):
        albumLabel.setParent(self.albumContainer)
        albumLabel.move(QPoint(self.nchild*albumLabel.width(), 0))
        self.albumLabels.append(albumLabel)
        self.nchild += 1
        self.albumContainer.setMinimumSize(self.nchild*albumLabel.width(), 0)
        albumLabel.show()

    # events
    def bindEvents(self):
        Application.mainWindow.windowResized.connect(self.windowResizeEvent)
        self.searchBox.textChanged.connect(self.textChanged)
        self.openButton.clicked.connect(self.openButtonClicked)

    def windowResizeEvent(self):
        mediaPlayer = Application.mainWindow.centralWidget()
        size = QSize(mediaPlayer.windowDecorations.width(), 0)
        self.navbarPadding.setMinimumSize(size)
        self.navbarPadding.resize(size)

    def textChanged(self, text):
        self.parentWidget().tableWidget.filterText = text
        self.parentWidget().tableWidget.sortAndFilter()

        if self.parentWidget().tableWidget.specialFilter:
            return

        self.nchild = 0
        for albumLabel in self.albumLabels:
            albumLabel.deleteLater()
        self.albumLabels.clear()

        albums = [v for k, v in Application.mainWindow.albums.items() if text in v.title.lower()]
        if not albums:
            self.albumScroll.hide()
            return
        self.albumScroll.show()
        albums.sort()

        if len(albums) <= 5:
            for album in albums:
                self.addAlbumLabel(AlbumLabel(self, album, text))
        else:
            albums = iter(albums)
            def iteration():
                if self.searchBox.text() != text:
                    return
                try:
                    self.addAlbumLabel(AlbumLabel(self, next(albums), text))
                    QTimer.singleShot(1, iteration)
                except StopIteration:
                    return
            iteration()

    def openButtonClicked(self):
        Application.mainWindow.setSong(self.searchBox.text())

    # album events
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            event.ignore()
        return False

    def wheelEvent(self, event):
        scrollBar = self.albumScroll.horizontalScrollBar()
        scrollBar.setValue(scrollBar.value()-event.angleDelta().y())

    # slots
    def toggleVisible(self):
        from .MediaPlayer import MediaPlayer
        if self.parentWidget().parentWidget().mode == MediaPlayer.FILE_LIST_MODE:
            self.setVisible(not self.isVisible())
        else:
            self.windowResizeEvent()
            self.parentWidget().parentWidget().setMode(MediaPlayer.FILE_LIST_MODE)
            self.show()
        if self.isVisible():
            self.searchBox.setFocus(True)
