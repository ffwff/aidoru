import os
from PyQt5.QtCore import QMimeDatabase
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

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

def imageMimetypeToExt(mimetype):
    if mimetype == "image/jpg":    return ".jpg"
    elif mimetype == "image/jpeg": return ".jpeg"
    elif mimetype == "image/png":  return ".png"
    elif mimetype == "image/bmp":  return ".bmp"
    elif mimetype == "image/gif":  return ".gif"
    return ""

def dropShadow():
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(15)
    effect.setXOffset(0)
    effect.setYOffset(3)
    effect.setColor(QColor(0, 0, 0, 30))
    return effect

def dropShadowUp():
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(10)
    effect.setXOffset(0)
    effect.setYOffset(-3)
    effect.setColor(QColor(0, 0, 0, 25))
    return effect
