from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class SearchView(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.initUI()
        self.bindEvents()

    def initUI(self):
        hboxLayout = QHBoxLayout()
        self.setLayout(hboxLayout)

        self.searchBox = searchBox = QLineEdit()
        hboxLayout.addWidget(searchBox)

    # events
    def bindEvents(self):
        self.searchBox.textChanged.connect(self.textChanged)

    def textChanged(self, text):
        self.parentWidget().tableWidget.filterText = text
        self.parentWidget().tableWidget.sortAndFilter()

    # slots
    def toggleVisible(self):
        from .MediaPlayer import MediaPlayer
        if self.parentWidget().parentWidget().mode == MediaPlayer.FILE_LIST_MODE:
            self.setVisible(not self.isVisible())
        else:
            self.parentWidget().parentWidget().setMode(MediaPlayer.FILE_LIST_MODE)
            self.show()
        if self.isVisible():
            self.searchBox.setFocus(True)
