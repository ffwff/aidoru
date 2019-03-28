from PyQt5.QtGui import QIcon
from PyQt5.QtWinExtras import *
from PyQt5.QtMultimedia import QMediaPlayer
from src.Application import Application
from src.modules.module import BaseModule

class KeyboardShortcutsModule(BaseModule):

    def __init__(self):
        BaseModule.__init__(self, "keyboardshortcuts", "Global keyboard shortcuts")

    def enable(self):
        BaseModule.enable(self)

    def disable(self):
        BaseModule.disable(self)
