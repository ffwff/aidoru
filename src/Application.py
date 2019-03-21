from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from urllib.request import urlopen
from src import __version__
import sys
import os

class Application(QApplication):

    def __init__(self, argv):
        QApplication.__init__(self, argv)

    def exec(self):
        from src.MainWindow import MainWindow
        Application.mainWindow = MainWindow()
        Application.mainWindow.initUI()
        return QApplication.exec()

    def update():
        def reexec():
            python = sys.executable
            if python: os.execl(python, python, *sys.argv)
            else: os.execl(sys.argv[0], sys.argv)
        execPath = os.path.join(os.path.dirname(__file__), "..")
        if os.path.isdir(os.path.join(execPath, ".git")) and 0:
            updateProcess = QProcess()
            updateProcess.setWorkingDirectory(execPath)
            updateProcess.start("git", ["git", "pull"])
            updateProcess.finished.connect(lambda exitCode, exitStatus: reexec())
        elif sys.platform == "win32" or True:
            try:
                release = urlopen("https://raw.githubusercontent.com/ffwff/aidoru/master/release.txt").read().decode("utf-8").strip()
            except:
                pass
            version, url = release.split(" ")
            if __version__ != version:
                updateProcess = QProcess()
                updateProcess.setWorkingDirectory(execPath)
                updateProcess.start("update.bat", ["update.bat"])
                updateProcess.finished.connect(lambda exitCode, exitStatus: reexec())
