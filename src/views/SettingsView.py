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

        # media location
        vboxLayout.addWidget(QLabel("Media Location"))

        self.musicLocationInput = musicLocationInput = QLineEdit()
        musicLocationInput.setText(MainWindow.instance.settings["mediaLocation"])
        vboxLayout.addWidget(musicLocationInput)

        self.musicRefreshButton = musicRefreshButton = QPushButton("Refresh media listing")
        vboxLayout.addWidget(musicRefreshButton)
        vboxLayout.setAlignment(musicRefreshButton, Qt.AlignRight)

        # file watcher
        self.fileWatcherOption = QCheckBox("File watcher")
        self.fileWatcherOption.setChecked(MainWindow.instance.settings["fileWatch"])
        vboxLayout.addWidget(self.fileWatcherOption)

        vboxLayout.addStretch(2)

    # events
    def bindEvents(self):
        self.musicRefreshButton.clicked.connect(self.musicRefreshButtonClicked)
        self.fileWatcherOption.stateChanged.connect(self.fileWatcherOptionChanged)

    def musicRefreshButtonClicked(self):
        mainWindow = MainWindow.instance
        mainWindow.settings["mediaLocation"] = self.musicLocationInput.text()
        mainWindow.saveSettings()
        mainWindow.repopulateMedias()

    def fileWatcherOptionChanged(self):
        mainWindow = MainWindow.instance
        mainWindow.settings["fileWatch"] = self.fileWatcherOption.isChecked()
        mainWindow.saveSettings()
        mainWindow.setWatchFiles()
