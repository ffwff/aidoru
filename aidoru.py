#!/usr/bin/env python3

from src.Application import Application
from PyQt5.QtWidgets import *
import sys
import os

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = Application(sys.argv)
    sys.exit(app.exec())
