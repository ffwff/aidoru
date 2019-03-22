from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import os
from src.Application import Application

class UpdateDialog(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.initUI()
        #self.bindEvents()

    # ui
    def initUI(self):
        self.setWindowTitle("updating!")
        self.setWindowFlags(Qt.Dialog)
        self.resize(QSize(320, 100))
        self.setMinimumSize(self.size())

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addStretch(1)

        label = QLabel("pls wait while we update")
        layout.addWidget(label)

        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        layout.addWidget(self.progressBar, 1)
        layout.addStretch(1)

    # events
    def downloadProgress(self, rx, total):
        self.progressBar.setValue(rx)
        self.progressBar.setMaximum(total)