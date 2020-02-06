from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from src.models.Settings import settings
from src.Application import Application
from src import __version__
from functools import partial

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
        vboxLayout.addWidget(QLabel("<b>User interface</b>"))

        layoutw = QWidget()
        layout = QVBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        self.darkThemeOption = QCheckBox("Dark theme")
        self.darkThemeOption.setChecked(settings.darkTheme)
        layout.addWidget(self.darkThemeOption)

        self.redrawBackgroundOption = QCheckBox("Redraw window background (requires restart)")
        self.redrawBackgroundOption.setChecked(settings.redrawBackground)
        layout.addWidget(self.redrawBackgroundOption)

        # media location
        vboxLayout.addWidget(QLabel("<b>Media Location</b>"))

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        self.musicLocationInput = musicLocationInput = QLineEdit()
        musicLocationInput.setText(settings.mediaLocation)
        layout.addWidget(musicLocationInput)

        self.musicLocationBrowse = musicLocationBrowse = QPushButton("Browse...")
        layout.addWidget(musicLocationBrowse)

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        # file watcher
        self.fileWatcherOption = QCheckBox("Watch file changes in this directory")
        self.fileWatcherOption.setChecked(settings.fileWatch)
        layout.addWidget(self.fileWatcherOption)

        layout.addStretch()

        self.musicRefreshButton = musicRefreshButton = QPushButton("Refresh media listing")
        layout.addWidget(musicRefreshButton)

        # updates
        vboxLayout.addWidget(QLabel("<b>Updates</b>"))

        layoutw = QWidget()
        layout = QHBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        layout.addWidget(QLabel("version " + __version__))

        self.checkUpdates = checkUpdates = QPushButton("Check for updates...")
        checkUpdates.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(checkUpdates)

        # modules
        vboxLayout.addWidget(QLabel("<b>Modules</b>"))

        layoutw = QWidget()
        layout = QVBoxLayout()
        layoutw.setLayout(layout)
        vboxLayout.addWidget(layoutw)

        for module in Application.modules:
            checkbox = QCheckBox(module.name)
            def stateChanged(_, state):
                checkbox, module = _
                if state == Qt.Unchecked:
                    module.disable()
                else:
                    module.enable()
                settings.modules[module.id] = module.enabled
                settings.save()
            def moduleStateChanged(checkbox, state):
                checkbox.blockSignals(True)
                checkbox.setCheckState(Qt.Checked if state else Qt.Unchecked)
                checkbox.blockSignals(False)
            checkbox.stateChanged.connect(partial(stateChanged, (checkbox, module)))
            module.connect(partial(moduleStateChanged, checkbox))
            layout.addWidget(checkbox)

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
        settings.darkTheme = self.darkThemeOption.isChecked()
        Application.mainWindow.setStyles()

    def redrawBackgroundOptionChanged(self):
        settings.redrawBackground = self.redrawBackgroundOption.isChecked()

    def musicLocationBrowseClicked(self):
        self.fileDialog = dialog = QFileDialog()
        dialog.setDirectory(settings.mediaLocation)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.fileSelected.connect(self.refreshMedia)
        dialog.show()

    def refreshMedia(self, dpath):
        settings.mediaLocation = dpath
        self.musicLocationInput.setText(dpath)
        Application.mainWindow.repopulateMedias()

    def fileWatcherOptionChanged(self):
        settings.fileWatch = self.fileWatcherOption.isChecked()
        Application.mainWindow.setWatchFiles()

class SettingsView(QScrollArea):

    def __init__(self):
        QScrollArea.__init__(self)
        self.form = SettingsForm()
        self.setWidget(self.form)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
