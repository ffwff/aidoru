from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from src.Application import Application
from src.utils import clearLayout

class AlbumLabel(QWidget):

    def __init__(self, parent, album):
        QWidget.__init__(self, parent)
        self.album = album
        self.initUI()

    def initUI(self):
        size = QSize(150, 200)
        self.setMinimumSize(size)
        self.setMaximumSize(size)
        self.resize(size)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.coverLabelContainer = coverLabelContainer = QWidget(self)
        coverLabelContainer.setObjectName("cover-label")
        coverLabelContainer.setMinimumSize(QSize(self.width(), self.width()))
        coverLabelContainerL = QHBoxLayout(coverLabelContainer)
        coverLabelContainerL.setSpacing(0)
        coverLabelContainerL.setContentsMargins(0, 0, 0, 0)
        coverLabelContainer.setLayout(coverLabelContainerL)
        layout.addWidget(coverLabelContainer)

        if self.album.image:
            self.coverLabel = coverLabel = QLabel(self)
            pixmap = QPixmap(self.album.image).scaledToWidth(self.width(), Qt.SmoothTransformation)
            coverLabel.setPixmap(pixmap)
            coverLabel.resize(pixmap.size())
            coverLabel.setAlignment(Qt.AlignCenter)
            coverLabelContainerL.addWidget(coverLabel)

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
        clayout.setContentsMargins(0,0,0,0)
        clayout.setSpacing(0)
        self.setLayout(clayout)
        container = QWidget()
        clayout.addWidget(container)
        vlayout = QVBoxLayout()
        container.setLayout(vlayout)

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vlayout.addWidget(layoutw)

        self.searchBox = searchBox = QLineEdit()
        layout.addWidget(searchBox)

        self.openButton = QPushButton(QIcon("./icons/find"), "open")
        layout.addWidget(self.openButton)

        #
        self.albumScroll = scrollArea = QScrollArea()
        scrollArea.hide()
        scrollArea.setMinimumSize(QSize(0, 200))
        scrollArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        scrollArea.setWidgetResizable(True)
        scrollArea.installEventFilter(self)
        vlayout.addWidget(scrollArea)

        layoutw = QWidget(scrollArea)
        scrollArea.setWidget(layoutw)
        self.albumLayout = layout = QHBoxLayout(layoutw)
        layoutw.setLayout(layout)
        layout.setContentsMargins(0,0,0,0)

    # events
    def bindEvents(self):
        self.searchBox.textChanged.connect(self.textChanged)
        self.openButton.clicked.connect(self.openButtonClicked)

    def textChanged(self, text):
        self.parentWidget().tableWidget.filterText = text
        self.parentWidget().tableWidget.sortAndFilter()

        clearLayout(self.albumLayout)
        albums = [v for k, v in Application.mainWindow.albums.items() if text in v.title.lower()]
        if not albums:
            self.albumScroll.hide()
            return
        self.albumScroll.show()
        albums.sort()
        if len(albums) <= 5:
            for album in albums:
                self.albumLayout.addWidget(AlbumLabel(self, album))
            self.albumLayout.addStretch()
        else:
            albums = iter(albums)
            def iteration():
                if self.searchBox.text() != text:
                    return
                try:
                    self.albumLayout.addWidget(AlbumLabel(self, next(albums)))
                    QTimer.singleShot(1, iteration)
                except StopIteration:
                    self.albumLayout.addStretch()
            iteration()

    def openButtonClicked(self):
        print(self.searchBox.text())
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
            self.parentWidget().parentWidget().setMode(MediaPlayer.FILE_LIST_MODE)
            self.show()
        if self.isVisible():
            self.searchBox.setFocus(True)
