from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.MainWindow as MainWindow

class SettingsView(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.initUI()
        self.bindEvents()

    # ui
    def initUI(self):
        vboxLayout = QVBoxLayout()
        self.setLayout(vboxLayout)

        vboxLayout.addStretch(1)

        self.musicLocationInput = musicLocationInput = QLineEdit()
        musicLocationInput.setText(MainWindow.instance.settings["mediaLocation"])
        vboxLayout.addWidget(musicLocationInput)

        self.musicRefreshButton = musicRefreshButton = QPushButton("Refresh media listing")
        vboxLayout.addWidget(musicRefreshButton)
        vboxLayout.setAlignment(musicRefreshButton, Qt.AlignRight)

        vboxLayout.addStretch(2)

    # events
    def bindEvents(self):
        self.musicRefreshButton.clicked.connect(self.musicRefreshButtonClicked)

    def musicRefreshButtonClicked(self):
        mainWindow = MainWindow.instance
        mainWindow.saveSettings()
        mainWindow.settings["mediaLocation"] = self.musicLocationInput.text()
        mainWindow.repopulateMedias()
