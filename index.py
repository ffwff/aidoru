from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class MiniPlayer(QWidget):


    def __init__(self, parent=None, microMode=False):
        QWidget.__init__(self, parent)

        self.setStyleSheet("""
QSlider{
margin-top:-6px;
}
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
        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(0)
        slider.setMaximum(1024)
        slider.setValue(512)
        slider.setTracking(True)

        albumLabel = QLabel("Album title")
        albumLabel.setAlignment(Qt.AlignCenter)

        if not microMode:
            artistLabel = QLabel("Artist name")
            artistLabel.setAlignment(Qt.AlignCenter)

        if microMode:
            vboxLayout.addWidget(slider)
        else:
            coverLabelContainer = QWidget(self)
            coverLabelContainer.setStyleSheet("background: #000;")
            coverLabelContainerL = QHBoxLayout(self)
            coverLabelContainerL.setSpacing(0)
            coverLabelContainerL.setContentsMargins(0, 0, 0, 0)
            coverLabelContainer.setLayout(coverLabelContainerL)

            coverLabelContainerL.addStretch()
            coverLabel = QLabel(coverLabelContainer)
            coverLabel.setPixmap(QPixmap.fromImage(QImage("./cover.jpg")).scaledToWidth(300, Qt.SmoothTransformation))
            coverLabel.setMinimumSize(QSize(300, 300))
            coverLabel.setMaximumSize(QSize(300, 300))
            coverLabelContainerL.addWidget(coverLabel)
            coverLabelContainerL.addStretch()
            vboxLayout.addWidget(coverLabelContainer)

            vboxLayout.addWidget(slider)
            vboxLayout.addStretch()
            vboxLayout.addWidget(albumLabel)
            albumLabel.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
            vboxLayout.addWidget(artistLabel)
            artistLabel.setStyleSheet("font-size: 12px; margin-bottom: 15px;")

        # buttons
        buttonsWidget = QWidget(self)
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
        vboxLayout.addWidget(buttonsWidget)

        backButton = QPushButton(QIcon.fromTheme("media-skip-backward"), "", self)

        ppButton = QPushButton(QIcon.fromTheme("media-playback-start"), "", self)

        forwardButton = QPushButton(QIcon.fromTheme("media-skip-forward"), "", self)

        if microMode:
            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)
            buttonsLayout.addStretch()
            buttonsLayout.addWidget(albumLabel)
            albumLabel.setStyleSheet("font-size: 12px;")
            buttonsLayout.addStretch()
        else:
            buttonsLayout.addStretch()
            buttonsLayout.addWidget(backButton)
            buttonsLayout.addWidget(ppButton)
            buttonsLayout.addWidget(forwardButton)
            buttonsLayout.addStretch()


        vboxLayout.addStretch()

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(300, 475))
        #self.setMinimumSize(QSize(300, 45))
        #self.setMaximumSize(QSize(300, 45))
        self.setWindowTitle("Hello world")
        self.setStyleSheet("background: #fff; color: #000;")

        self.centralWidget = MiniPlayer(self, False)
        self.setCentralWidget(self.centralWidget)

app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
