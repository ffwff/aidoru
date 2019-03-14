from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import src.MainWindow as MainWindow

class MediaLabel(QLabel):

    def __init__(self, media, parent):
        QLabel.__init__(self, parent)

        self.media = media
        self.initUI()

    # ui
    def initUI(self):
        self.setWordWrap(True)
        self.setText(
"""
<table>
<tr>
    <td width='80%%' style='max-width: 80%%;'>%s</td>
    <td width='20%%' style='max-width: 20%%;text-align: right;'>%s</td>
</tr>
%s
</table>
""" % (self.media.title, self.media.duration.strftime("%M:%S"),
"""
<tr>
    <td colspan='2'>%s</td>
</tr>
""" % (self.media.artist,) if self.media.artist else ""))

    # activity
    def setActive(self, active):
        if active:
            self.setProperty("class", "active")
        else:
            self.setProperty("class", "")

    # events
    def mousePressEvent(self, e):
        MainWindow.instance.setSong(self.media.path)
