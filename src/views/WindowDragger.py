from PyQt5.QtCore import *
from src.Application import Application

class WindowDragger():

    def mousePressEvent(self, event):
        self.mpos = event.pos()

    def mouseReleaseEvent(self, event):
        del self.mpos

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.mpos:
            diff = event.pos() - self.mpos
            Application.mainWindow.move(Application.mainWindow.pos() + diff)
