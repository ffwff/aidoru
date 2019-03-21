from PyQt5.QtWidgets import *
from urllib.request import urlopen
import sys

class Application(QApplication):

    def __init__(self, argv):
        QApplication.__init__(self, argv)

    def exec(self):
        from src.MainWindow import MainWindow
        Application.mainWindow = MainWindow()
        Application.mainWindow.initUI()
        return QApplication.exec()

    def update():
        execPath = os.path.join(os.path.dirname(__file__), "..")
        if os.path.isdir(os.path.join(execPath, ".git")):
            def finished(exitCode, exitStatus):
                python = sys.executable
                os.execl(python, python, *sys.argv)
            self.updateProcess = updateProcess = QProcess()
            update_process.setWorkingDirectory(execPath)
            update_process.start("git", ["git", "pull"])
            update_process.finished.connect(finished)
        elif sys.platform == "win32":
            latest = urlopen("https://raw.githubusercontent.com/ffwff/aidoru/master/release.txt").read()
            #print(latest)
