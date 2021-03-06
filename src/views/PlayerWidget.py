from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
from src.Application import Application
from src.utils import dropShadow, dropShadowUp
from .WindowDragger import WindowDragger

class PlayerWidget(WindowDragger, QWidget):

    # modes
    MAIN_MODE   = 0
    MICRO_MODE  = 1
    WIDGET_MODE = 2

    def __init__(self, parent=None, mode=MAIN_MODE):
        QWidget.__init__(self, parent)

        self.mode = mode
        self.mpos = None
        self.setAcceptDrops(True)
        self.initUI()

        # events
        self.stateChanged(Application.mainWindow.media.state())
        if hasattr(self, "volumeButton"):
            self.mutedChanged(Application.mainWindow.media.isMuted())
        self.bindEvents()

    def initUI(self):
        if self.mode == PlayerWidget.MAIN_MODE:
            self.setProperty("class", "main-mode")
        elif self.mode == PlayerWidget.MICRO_MODE:
            self.setProperty("class", "micro-mode")
        elif self.mode == PlayerWidget.WIDGET_MODE:
            self.setProperty("class", "widget-mode")

        vboxLayout = QVBoxLayout(self)
        vboxLayout.setContentsMargins(0, 0, 0, 0)
        vboxLayout.setSpacing(0)
        self.setLayout(vboxLayout)

        # song info
        self.positionSlider = slider = QSlider(Qt.Horizontal)
        slider.setObjectName("position-slider")
        slider.setTracking(True)

        self.albumLabel = albumLabel = QLabel("not playing")
        albumLabel.setObjectName("album-label")
        albumLabel.setAlignment(Qt.AlignCenter)

        if self.mode == PlayerWidget.MAIN_MODE:
            self.artistLabel = artistLabel = QLabel("no name")
            artistLabel.setAlignment(Qt.AlignCenter)

        if self.mode == PlayerWidget.MICRO_MODE:
            vboxLayout.addWidget(slider)
        elif self.mode == PlayerWidget.MAIN_MODE:
            self.coverLabelContainer = coverLabelContainer = QWidget(self)
            coverLabelContainer.setObjectName("cover-label")
            coverLabelContainerL = QHBoxLayout(self)
            coverLabelContainerL.setContentsMargins(0, 0, 0, 0)
            coverLabelContainerL.setSpacing(0)
            coverLabelContainer.setLayout(coverLabelContainerL)

            self.coverLabel = coverLabel = QLabel(coverLabelContainer)
            coverLabel.setAlignment(Qt.AlignCenter)
            coverLabelContainerL.addWidget(coverLabel)
            vboxLayout.addWidget(coverLabelContainer)

            vboxLayout.addWidget(slider)
            vboxLayout.addStretch()
            vboxLayout.addWidget(albumLabel)
            vboxLayout.addWidget(artistLabel)
            artistLabel.setObjectName("artist-label")

        # buttons
        buttonsWidget = QWidget()
        buttonsWidget.setProperty("class", "buttons-widget")

        buttonsLayout = QHBoxLayout(self)
        buttonsLayout.setContentsMargins(10, 0, 10, 0)
        buttonsLayout.setSpacing(0)
        buttonsWidget.setLayout(buttonsLayout)

        self.backButton = backButton = QPushButton(QIcon("./icons/media-skip-backward"), "")

        self.ppButton = ppButton = QPushButton()

        self.forwardButton = forwardButton = QPushButton(QIcon("./icons/media-skip-forward"), "")

        if self.mode == PlayerWidget.MICRO_MODE:
            vboxLayout.addWidget(buttonsWidget)
            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)
            buttonsLayout.addStretch()
            buttonsLayout.addWidget(albumLabel)
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
            vboxLayout.addWidget(buttonsWidget)

            buttonsLayout.setContentsMargins(0,0,5,5)
            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)

            layoutw = QWidget()
            layoutw.setMinimumSize(QSize(0,50))
            layoutw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            layout = QVBoxLayout()
            layout.setContentsMargins(10,16,10,0)
            layout.setSpacing(0)
            layoutw.setLayout(layout)
            buttonsLayout.addWidget(layoutw)

            layout.addWidget(slider)
            layout.addWidget(albumLabel)

            self.volumeButton = volumeButton = QPushButton()
            buttonsLayout.addWidget(volumeButton)
            self.volumeSlider = volumeSlider = QSlider(Qt.Horizontal)
            volumeSlider.setObjectName("volume-slider")
            volumeSlider.setMinimum(0)
            volumeSlider.setMaximum(100)
            volumeSlider.setValue(Application.mainWindow.media.volume())
            buttonsLayout.addWidget(volumeSlider)

            buttonsWidget.setGraphicsEffect(dropShadowUp())
            buttonsWidget.setFixedHeight(buttonsWidget.sizeHint().height())
            self.setFixedHeight(buttonsWidget.sizeHint().height()+buttonsWidget.graphicsEffect().blurRadius())

    def setMode(self, mode):
        self.mode = mode
        self.initUI()

    def bindEvents(self):
        media = Application.mainWindow.media

        # song info
        Application.mainWindow.songInfoChanged.connect(self.updateInfo)
        ## pos slider
        media.durationChanged.connect(self.durationChanged)
        media.positionChanged.connect(self.positionChanged)
        media.volumeChanged.connect(self.volumeChanged)
        self.positionSlider.valueChanged.connect(self.positionSliderChanged)

        # controls button
        self.backButton.clicked.connect(Application.mainWindow.prevSong)
        self.forwardButton.clicked.connect(Application.mainWindow.nextSong)
        self.ppButton.clicked.connect(Application.mainWindow.playPause)
        media.stateChanged.connect(self.stateChanged)
        if hasattr(self, "volumeButton"):
            self.volumeButton.clicked.connect(self.volumeButtonClicked)
            media.mutedChanged.connect(self.mutedChanged)
        if hasattr(self, "volumeSlider"):
            self.volumeSlider.valueChanged.connect(self.volumeSliderChanged)

        # misc
        media.error.connect(self.mediaError)

    # events
    def mouseMoveEvent(self, event):
        if not self.positionSlider.geometry().contains(event.pos()):
            WindowDragger.mouseMoveEvent(self, event)

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
        Application.mainWindow.media.setPosition(position)

    ## volume slider
    def volumeChanged(self, volume):
        self.volumeSlider.blockSignals(True)
        self.volumeSlider.setValue(volume)
        self.volumeSlider.blockSignals(False)

    ## controls
    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.ppButton.setIcon(QIcon("./icons/media-playback-pause"))
        else:
            self.ppButton.setIcon(QIcon("./icons/media-playback-start"))

    ## volume mute
    def mutedChanged(self, muted):
        if muted:
            self.volumeButton.setIcon(QIcon("./icons/audio-volume-muted"))
        else:
            self.volumeButton.setIcon(QIcon("./icons/audio-volume-high"))

    def volumeButtonClicked(self):
        media = Application.mainWindow.media
        media.setMuted(not media.isMuted())

    ## volume slider
    def volumeSliderChanged(self, volume):
        Application.mainWindow.media.setVolume(volume)

    # ui elements
    def updateInfo(self, mediaInfo):
        if hasattr(self, "artistLabel"):
            self.albumLabel.setText(mediaInfo.title)
            self.artistLabel.setText(mediaInfo.artist if mediaInfo.artist else "<i>unknown</i>")
        else:
            if mediaInfo.artist:
                self.albumLabel.setText(mediaInfo.title + " − " + mediaInfo.artist)
            else:
                self.albumLabel.setText(mediaInfo.title)
        if hasattr(self, "coverLabel"):
            pixmap = QPixmap(mediaInfo.image).scaledToWidth(320, Qt.SmoothTransformation)
            self.coverLabel.setPixmap(pixmap)
            self.coverLabel.resize(pixmap.size())
            size = QSize(pixmap.width(), self.coverLabel.height())
            self.coverLabelContainer.setMinimumSize(size)
            self.coverLabelContainer.resize(size)
            Application.mainWindow.resize(size)
