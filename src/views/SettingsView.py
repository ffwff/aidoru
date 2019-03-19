from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.Application import Application

class SettingsView(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.fileDialog = None
        self.initUI()
        self.bindEvents()

    # ui
    def initUI(self):
        vboxLayout = QVBoxLayout()
        self.setContentsMargins(100, 0, 100, 0)
        self.setLayout(vboxLayout)

        vboxLayout.addStretch(1)

        # ui options
        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        self.redrawBackgroundOption = QCheckBox("Redraw window background (requires restart)")
        self.redrawBackgroundOption.setChecked(Application.mainWindow.settings["redrawBackground"])
        layout.addWidget(self.redrawBackgroundOption)

        # media location
        vboxLayout.addWidget(QLabel("Media Location"))

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        self.musicLocationInput = musicLocationInput = QLineEdit()
        musicLocationInput.setText(Application.mainWindow.settings["mediaLocation"])
        layout.addWidget(musicLocationInput)

        self.musicLocationBrowse = musicLocationBrowse = QPushButton("Browse...")
        layout.addWidget(musicLocationBrowse)

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        # file watcher
        self.fileWatcherOption = QCheckBox("Watch file changes in this directory")
        self.fileWatcherOption.setChecked(Application.mainWindow.settings["fileWatch"])
        layout.addWidget(self.fileWatcherOption)

        layout.addStretch()

        self.musicRefreshButton = musicRefreshButton = QPushButton("Refresh media listing")
        layout.addWidget(musicRefreshButton)

        vboxLayout.addStretch(2)

    # events
    def bindEvents(self):
        self.musicLocationBrowse.clicked.connect(self.musicLocationBrowseClicked)
        self.musicRefreshButton.clicked.connect(lambda: self.refreshMedia(self.musicLocationInput.text()))
        self.fileWatcherOption.stateChanged.connect(self.fileWatcherOptionChanged)
        self.redrawBackgroundOption.stateChanged.connect(self.redrawBackgroundOptionChanged)

    def musicLocationBrowseClicked(self):
        self.fileDialog = dialog = QFileDialog()
        dialog.setDirectory(Application.mainWindow.settings["mediaLocation"])
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.fileSelected.connect(self.refreshMedia)
        dialog.show()

    def refreshMedia(self, dpath):
        mainWindow = Application.mainWindow
        mainWindow.settings["mediaLocation"] = dpath
        self.musicLocationInput.setText(dpath)
        mainWindow.saveSettings()
        mainWindow.repopulateMedias()

    def fileWatcherOptionChanged(self):
        mainWindow = Application.mainWindow
        mainWindow.settings["fileWatch"] = self.fileWatcherOption.isChecked()
        mainWindow.saveSettings()
        mainWindow.setWatchFiles()

    def redrawBackgroundOptionChanged(self):
        mainWindow = Application.mainWindow
        mainWindow.settings["redrawBackground"] = self.redrawBackgroundOption.isChecked()
        mainWindow.saveSettings()
