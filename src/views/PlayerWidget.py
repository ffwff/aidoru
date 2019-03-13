from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimedia import *
import src.MainWindow as MainWindow

class PlayerWidget(QWidget):

    # modes
    MAIN_MODE   = 0
    MICRO_MODE  = 1
    WIDGET_MODE = 2

    def __init__(self, parent=None, mode=MAIN_MODE):
        QWidget.__init__(self, parent)

        # media player
        self.mode = mode
        self.setAcceptDrops(True)

        # ui elements
        self.initUI()

        # events
        self.stateChanged(MainWindow.instance.media.state())
        if hasattr(self, "volumeButton"):
            self.mutedChanged(MainWindow.instance.media.isMuted())
        self.bindEvents()

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

        self.albumLabel = albumLabel = QLabel("no title")
        albumLabel.setAlignment(Qt.AlignCenter)

        if self.mode == PlayerWidget.MAIN_MODE:
            self.artistLabel = artistLabel = QLabel("no name")
            artistLabel.setAlignment(Qt.AlignCenter)

        if self.mode == PlayerWidget.MICRO_MODE:
            vboxLayout.addWidget(slider)
        elif self.mode == PlayerWidget.MAIN_MODE:
            self.coverLabelContainer = coverLabelContainer = QWidget(self)
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
            albumLabel.setStyleSheet("font-size: 12px;")
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
            volumeSlider.setMaximum(100)
            volumeSlider.setValue(100)
            buttonsLayout.addWidget(volumeSlider)

    def setMode(self, mode):
        self.mode = mode
        self.initUI()

    def bindEvents(self):
        media = MainWindow.instance.media

        # song info
        MainWindow.instance.songInfoChanged.connect(self.updateInfo)
        ## pos slider
        media.durationChanged.connect(self.durationChanged)
        media.positionChanged.connect(self.positionChanged)
        self.positionSlider.valueChanged.connect(self.positionSliderChanged)

        # controls button
        self.backButton.clicked.connect(self.backButtonClicked)
        self.ppButton.clicked.connect(MainWindow.instance.playPause)
        media.stateChanged.connect(self.stateChanged)
        self.forwardButton.clicked.connect(self.forwardButtonClicked)
        if hasattr(self, "volumeButton"):
            self.volumeButton.clicked.connect(self.volumeButtonClicked)
            media.mutedChanged.connect(self.mutedChanged)
        if hasattr(self, "volumeSlider"):
            self.volumeSlider.valueChanged.connect(self.volumeSliderChanged)

        # misc
        media.error.connect(self.mediaError)

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
        MainWindow.instance.media.setPosition(position)

    ## controls
    def backButtonClicked(self):
        MainWindow.instance.albumPrev()

    def forwardButtonClicked(self):
        MainWindow.instance.albumNext()

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
        media = MainWindow.instance.media
        media.setMuted(not media.isMuted())

    ## volume slider
    def volumeSliderChanged(self, volume):
        MainWindow.instance.media.setVolume(volume)

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
            pixmap = QPixmap.fromImage(QImage(mediaInfo.image)) \
                .scaledToWidth(self.coverLabel.width(), Qt.SmoothTransformation)
            self.coverLabel.setPixmap(pixmap)
            self.coverLabelContainer.resize(QSize(self.coverLabel.width(), pixmap.height()))
