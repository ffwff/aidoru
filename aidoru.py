from src.MainWindow import MainWindow
from PyQt5.QtWidgets import *
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow().show()
    sys.exit(app.exec())
