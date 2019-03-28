#!/usr/bin/env python3

from src.Application import Application
from PyQt5.QtWidgets import *
import sys
import os

def excepthook(type, value, tb):
    import traceback
    traceback.print_tb(tb)
    print(repr(value))
    response = QMessageBox.warning(Application.mainWindow, "Error", repr(value), QMessageBox.Ok | QMessageBox.Close)
    if response != QMessageBox.Ok:
        sys.exit(1)

sys.excepthook = excepthook

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = Application(sys.argv)
    sys.exit(app.exec())
