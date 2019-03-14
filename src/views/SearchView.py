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
        self.setVisible(not self.isVisible())
        if self.isVisible():
            self.searchBox.setFocus(True)
