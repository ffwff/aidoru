from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(300, 475))
        self.setWindowTitle("Hello world")

        centralWidget = QWidget(self)
        centralWidget.setStyleSheet("""
QWidget {
    background: #fff;
    color: #000;
}
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
        self.setCentralWidget(centralWidget)
        vboxLayout = QVBoxLayout(self)
        vboxLayout.setContentsMargins(0, 0, 0, 0)
        vboxLayout.setSpacing(0)
        centralWidget.setLayout(vboxLayout)

        # song info
        coverLabelContainer = QWidget(self)
        coverLabelContainer.setStyleSheet("background: #000;")
        coverLabelContainerL = QHBoxLayout(self)
        coverLabelContainerL.setSpacing(0)
        coverLabelContainerL.setContentsMargins(0, 0, 0, 0)
        coverLabelContainer.setLayout(coverLabelContainerL)
        vboxLayout.addWidget(coverLabelContainer)

        coverLabelContainerL.addStretch()
        coverLabel = QLabel(coverLabelContainer)
        coverLabel.setPixmap(QPixmap.fromImage(QImage("./cover.jpg")).scaledToWidth(300, Qt.SmoothTransformation))
        coverLabel.setMinimumSize(QSize(300, 300))
        coverLabel.setMaximumSize(QSize(300, 300))
        coverLabelContainerL.addWidget(coverLabel)
        coverLabelContainerL.addStretch()

        slider = QSlider(Qt.Horizontal, self)
        slider.setMinimum(0)
        slider.setMaximum(1024)
        slider.setValue(512)
        slider.setTracking(True)
        vboxLayout.addWidget(slider)

        vboxLayout.addStretch()

        albumLabel = QLabel("Album title", self)
        albumLabel.setStyleSheet("font-size: 16px; margin-bottom: 5px;")
        albumLabel.setAlignment(Qt.AlignCenter)
        vboxLayout.addWidget(albumLabel)

        artistLabel = QLabel("Artist name", self)
        artistLabel.setStyleSheet("font-size: 12px; margin-bottom: 15px;")
        artistLabel.setAlignment(Qt.AlignCenter)
        vboxLayout.addWidget(artistLabel)

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
        buttonsLayout.addStretch()

        backButton = QPushButton(QIcon.fromTheme("media-skip-backward"), "", self)
        buttonsLayout.addWidget(backButton)

        ppButton = QPushButton(QIcon.fromTheme("media-playback-start"), "", self)
        buttonsLayout.addWidget(ppButton)

        forwardButton = QPushButton(QIcon.fromTheme("media-skip-forward"), "", self)
        buttonsLayout.addWidget(forwardButton)

        buttonsLayout.addStretch()

        vboxLayout.addStretch()

app = QApplication(sys.argv)
win = MainWindow()
win.show()
sys.exit(app.exec())
