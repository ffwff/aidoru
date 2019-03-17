from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import src.MainWindow as MainWindow

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

        # media location
        vboxLayout.addWidget(QLabel("Media Location"))

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        self.musicLocationInput = musicLocationInput = QLineEdit()
        musicLocationInput.setText(MainWindow.instance.settings["mediaLocation"])
        layout.addWidget(musicLocationInput)

        self.musicLocationBrowse = musicLocationBrowse = QPushButton("Browse...")
        layout.addWidget(musicLocationBrowse)

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        # file watcher
        self.fileWatcherOption = QCheckBox("Watch file changes in this directory")
        self.fileWatcherOption.setChecked(MainWindow.instance.settings["fileWatch"])
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

    def musicLocationBrowseClicked(self):
        self.fileDialog = dialog = QFileDialog()
        dialog.setDirectory(MainWindow.instance.settings["mediaLocation"])
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.fileSelected.connect(self.refreshMedia)
        dialog.show()

    def refreshMedia(self, dpath):
        mainWindow = MainWindow.instance
        mainWindow.settings["mediaLocation"] = dpath
        self.musicLocationInput.setText(dpath)
        mainWindow.saveSettings()
        mainWindow.repopulateMedias()

    def fileWatcherOptionChanged(self):
        mainWindow = MainWindow.instance
        mainWindow.settings["fileWatch"] = self.fileWatcherOption.isChecked()
        mainWindow.saveSettings()
        mainWindow.setWatchFiles()
