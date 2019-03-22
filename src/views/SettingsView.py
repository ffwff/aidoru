from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.Application import Application
from src import __version__

class SettingsForm(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.fileDialog = None
        self.initUI()
        self.bindEvents()

    # ui
    def initUI(self):
        vboxLayout = QVBoxLayout()
        vboxLayout.setContentsMargins(100, 20, 100, 0)
        self.setLayout(vboxLayout)

        vboxLayout.addStretch(1)

        # ui options
        vboxLayout.addWidget(QLabel("User interface"))

        layoutw = QWidget()
        layout = QVBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        self.darkThemeOption = QCheckBox("Dark theme")
        self.darkThemeOption.setChecked(Application.mainWindow.settings["darkTheme"])
        layout.addWidget(self.darkThemeOption)

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

        # updates
        vboxLayout.addWidget(QLabel("Updates"))

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        layout.addWidget(QLabel("version " + __version__))

        self.checkUpdates = checkUpdates = QPushButton("Check for updates...")
        checkUpdates.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(checkUpdates)

        vboxLayout.addStretch(2)

    # events
    def bindEvents(self):
        self.darkThemeOption.stateChanged.connect(self.darkThemeOptionChanged)
        self.redrawBackgroundOption.stateChanged.connect(self.redrawBackgroundOptionChanged)
        self.musicLocationBrowse.clicked.connect(self.musicLocationBrowseClicked)
        self.musicRefreshButton.clicked.connect(lambda: self.refreshMedia(self.musicLocationInput.text()))
        self.fileWatcherOption.stateChanged.connect(self.fileWatcherOptionChanged)
        self.checkUpdates.clicked.connect(Application.update)

    def darkThemeOptionChanged(self):
        mainWindow = Application.mainWindow
        mainWindow.settings["darkTheme"] = self.darkThemeOption.isChecked()
        mainWindow.saveSettings()
        mainWindow.setStyles()

    def redrawBackgroundOptionChanged(self):
        mainWindow = Application.mainWindow
        mainWindow.settings["redrawBackground"] = self.redrawBackgroundOption.isChecked()
        mainWindow.saveSettings()

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

class SettingsView(QScrollArea):

    def __init__(self):
        QScrollArea.__init__(self)
        self.form = SettingsForm()
        self.setWidget(self.form)
        self.setWidgetResizable(True)
