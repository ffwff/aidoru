#!/usr/bin/env python3

from src.Application import Application
from PyQt5.QtWidgets import *
import sys

if __name__ == "__main__":
    app = Application(sys.argv)
    sys.exit(app.exec())
