from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
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
        self = Application
        execPath = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
        from .views.UpdateDialog import UpdateDialog
        if os.path.isdir(os.path.join(execPath, ".git")):
            self.updateProcess = updateProcess = QProcess()
            updateProcess.setWorkingDirectory(execPath)
            updateProcess.start("git", ["git", "pull"])
            def finished(exitCode, exitStatus):
                python = sys.executable
                if python: os.execl(python, python, *sys.argv)
                else: os.execl(sys.argv[0], sys.argv)
            updateProcess.finished.connect(finished)
        elif sys.platform == "win32":
            try:
               release = urlopen("https://raw.githubusercontent.com/ffwff/aidoru/master/release.txt").read().decode("utf-8").strip()
            except:
                return
            version, url = release.split(" ")
            if __version__ != version:
                url = urlopen(url).geturl() # qt doesn't handle redirections
                self.updateDialog = UpdateDialog()
                self.updateDialog.show()
                self.updateRequest = QNetworkRequest(QUrl(url))

                f = open(os.path.join(execPath, "aidoru.zip"), "wb")
                def downloadRead():
                    f.write(self.updateReply.readAll())
                def finished():
                    updateProcess = QProcess()
                    updateProcess.startDetached("powershell.exe", ["powershell.exe", "-Command",
r"""
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Unzip {
    param([string]$zipfile, [string]$outpath)
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipfile, $outpath)
}
$folder=New-TemporaryFile | %%{ rm $_; mkdir $_ }
$path="%s"
echo "$path\aidoru.zip"
Unzip "$path\aidoru.zip" $folder
xcopy "$folder\aidoru" $path /k /q /y /c /e
Start-Process "%s"
""" % (execPath, sys.argv[0])])
                    sys.exit(0)

                self.networkManager = QNetworkAccessManager()
                self.updateReply = reply = self.networkManager.get(self.updateRequest)
                reply.downloadProgress.connect(self.updateDialog.downloadProgress)
                reply.finished.connect(finished)
                reply.readyRead.connect(downloadRead)

