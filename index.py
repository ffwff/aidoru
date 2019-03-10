from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtMultimedia import *
import sys

# base player widget
class PlayerWidget(QWidget):

    # modes
    MAIN_MODE   = 0
    MICRO_MODE  = 1
    WIDGET_MODE = 2

    def __init__(self, parent=None, mode=MAIN_MODE):
        QWidget.__init__(self, parent)

        # media player
        mediaContent = QMediaContent(QUrl(""))
        self.media = QMediaPlayer()
        self.media.setMedia(mediaContent)
        self.mode = mode

        # ui elements
        self.setStyleSheet("""
QSlider::groove:horizontal {
    height: 6px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: #c4c4c4;
    margin: 0 0;
}
QSlider::sub-page:horizontal {
    background: red;
    border-radius: 4px;
}
QSlider::handle:horizontal {
    background: blue;
    width: 6px;
    border-radius: 100%;
}
""")
        vboxLayout = QVBoxLayout(self)
        vboxLayout.setContentsMargins(0, 0, 0, 0)
        vboxLayout.setSpacing(0)
        self.setLayout(vboxLayout)

        # song info
        self.positionSlider = slider = QSlider(Qt.Horizontal)
        slider.setTracking(True)
        if mode != PlayerWidget.WIDGET_MODE:
            slider.setStyleSheet("margin-top:-6px;")

        self.albumLabel = albumLabel = QLabel("Album title")
        albumLabel.setAlignment(Qt.AlignCenter)

        if mode == PlayerWidget.MAIN_MODE:
            self.artistLabel = artistLabel = QLabel("Artist name")
            artistLabel.setAlignment(Qt.AlignCenter)
        else:
            albumLabel.setText("Artist title − Artist name")

        if mode == PlayerWidget.MICRO_MODE:
            vboxLayout.addWidget(slider)
        elif mode == PlayerWidget.MAIN_MODE:
            coverLabelContainer = QWidget(self)
            coverLabelContainer.setStyleSheet("background: #000;")
            coverLabelContainerL = QHBoxLayout(self)
            coverLabelContainerL.setSpacing(0)
            coverLabelContainerL.setContentsMargins(0, 0, 0, 0)
            coverLabelContainer.setLayout(coverLabelContainerL)

            self.coverLabel = coverLabel = QLabel(coverLabelContainer)
            coverLabel.setAlignment(Qt.AlignCenter)
            coverLabel.setPixmap(QPixmap.fromImage(QImage("./cover.jpg")).scaledToWidth(300, Qt.SmoothTransformation))
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

        self.backButton = backButton = QPushButton(QIcon.fromTheme("media-skip-backward"), "")

        self.ppButton = ppButton = QPushButton()

        self.forwardButton = forwardButton = QPushButton(QIcon.fromTheme("media-skip-forward"), "")

        if mode == PlayerWidget.MICRO_MODE:
            vboxLayout.addWidget(buttonsWidget)
            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)
            buttonsLayout.addStretch()
            buttonsLayout.addWidget(albumLabel)
            albumLabel.setStyleSheet("font-size: 12px;")
            buttonsLayout.addStretch()
        elif mode == PlayerWidget.MAIN_MODE:
            vboxLayout.addWidget(buttonsWidget)
            buttonsLayout.addStretch()
            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)
            buttonsLayout.addStretch()

        if mode != PlayerWidget.WIDGET_MODE:
            vboxLayout.addStretch()

        # widget mode - separated because it's fundamentally different
        if mode == PlayerWidget.WIDGET_MODE:
            vboxLayout.addStretch()

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
            volumeSlider.setMaximum(200)
            volumeSlider.setValue(100)
            buttonsLayout.addWidget(volumeSlider)

            vboxLayout.addStretch()

        # events
        self.stateChanged(self.media.state())
        self.mutedChanged(self.media.isMuted())
        self.bindEvents()

    def bindEvents(self):
        # song info
        ## pos slider
        self.media.durationChanged.connect(self.durationChanged)
        self.media.positionChanged.connect(self.positionChanged)
        self.positionSlider.valueChanged.connect(self.positionSliderChanged)

        # controls button
        self.backButton.clicked.connect(self.backButtonClicked)
        self.ppButton.clicked.connect(self.ppButtonClicked)
        self.media.stateChanged.connect(self.stateChanged)
        self.forwardButton.clicked.connect(self.forwardButtonClicked)
        if hasattr(self, "volumeButton"):
            self.volumeButton.clicked.connect(self.volumeButtonClicked)
            self.media.mutedChanged.connect(self.mutedChanged)
        if hasattr(self, "volumeSlider"):
            self.volumeSlider.valueChanged.connect(self.volumeSliderChanged)

    # events
    ## position slider
    def durationChanged(self, duration):
        self.positionSlider.setMaximum(duration)

    def positionChanged(self, position):
        self.positionSlider.blockSignals(True)
        self.positionSlider.setValue(position)
        self.positionSlider.blockSignals(False)

    def positionSliderChanged(self, position):
        self.media.setPosition(position)

    ## controls
    def backButtonClicked(self):
        raise NotImplementedError

    def ppButtonClicked(self):
        if self.media.state() == QMediaPlayer.PlayingState:
            self.media.pause()
        else:
            self.media.play()
    def stateChanged(self, state):
        if state == QMediaPlayer.PlayingState:
            self.ppButton.setIcon(QIcon.fromTheme("media-playback-pause"))
        else:
            self.ppButton.setIcon(QIcon.fromTheme("media-playback-start"))

    def forwardButtonClicked(self):
        raise NotImplementedError

    ## volume mute
    def mutedChanged(self, muted):
        if muted:
            self.volumeButton.setIcon(QIcon.fromTheme("audio-volume-muted"))
        else:
            self.volumeButton.setIcon(QIcon.fromTheme("audio-volume-high"))

    def volumeButtonClicked(self):
        self.media.setMuted(not self.media.isMuted())

    ## volume slider
    def volumeSliderChanged(self, volume):
        self.media.setVolume(volume)

# application widget
class MediaPlayer(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        self.playerWidget = PlayerWidget(self, PlayerWidget.WIDGET_MODE)
        vboxLayout.addWidget(self.playerWidget)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(1200, 900))
        #self.setMinimumSize(QSize(300, 475))
        #self.setMinimumSize(QSize(300, 45))
        #self.setMaximumSize(QSize(300, 45))
        self.setWindowTitle("Hello world")
        self.setStyleSheet("background: #fff; color: #000;")

        #self.centralWidget = PlayerWidget(self, PlayerWidget.MAIN_MODE)
        self.centralWidget = MediaPlayer(self)
        self.setCentralWidget(self.centralWidget)

app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
