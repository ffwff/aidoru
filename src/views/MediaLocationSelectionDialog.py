from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from src.Application import Application

class MediaLocationSelectionDialog(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.initUI()
        self.bindEvents()

    # ui
    def initUI(self):
        self.setWindowTitle("oopsie woopsie!")
        self.setWindowFlags(Qt.Dialog)
        self.resize(QSize(320, 120))
        self.setMinimumSize(self.size())

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(QWidget(), 0, 0)
        layout.setRowStretch(0,1)

        label = QLabel("Please choose a valid music directory:")
        layout.addWidget(label, 1, 0, 1, 2)

        self.musicLocationInput = musicLocationInput = QLineEdit()
        musicLocationInput.setText(Application.mainWindow.settings["mediaLocation"])
        layout.addWidget(musicLocationInput, 2, 0)

        self.musicLocationBrowse = musicLocationBrowse = QPushButton("Browse...")
        layout.addWidget(musicLocationBrowse, 2, 1)
        layout.setColumnStretch(0, 1)

        layout.addWidget(QWidget(), 3, 0)
        layout.setRowStretch(3,1)

        self.okButton = QPushButton("OK")
        self.okButton.setEnabled(os.path.isdir(Application.mainWindow.settings["mediaLocation"]))
        layout.addWidget(self.okButton, 4, 0, 1, 2, Qt.AlignRight)

    # events
    def bindEvents(self):
        self.musicLocationBrowse.clicked.connect(self.musicLocationBrowseClicked)

    def musicLocationBrowseClicked(self):
        self.fileDialog = dialog = QFileDialog()
        dialog.setDirectory(Application.mainWindow.settings["mediaLocation"])
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.fileSelected.connect(self.refreshMedia)
        dialog.show()

    def refreshMedia(self, dpath):
        if os.path.isdir(dpath):
            mainWindow = Application.mainWindow
            mainWindow.settings["mediaLocation"] = dpath
            self.musicLocationInput.setText(dpath)
            mainWindow.saveSettings()
            self.okButton.setEnabled(True)
        else:
            self.okButton.setEnabled(False)
