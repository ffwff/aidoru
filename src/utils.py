import os
from PyQt5.QtCore import QMimeDatabase

def pathUp(path):
    if path.startswith("file://"):
        return os.path.normpath(os.path.join(path[7:], ".."))
    return os.path.normpath(os.path.join(path, ".."))

def clearLayout(layout):
    while layout.count():
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()

mimeDatabase = QMimeDatabase()
def getFileType(f):
    mime = mimeDatabase.mimeTypesForFileName(f)
    if not mime: return ""
    return mime[0].name().split("/")[0]
