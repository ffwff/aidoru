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
        execPath = os.path.join(os.path.dirname(__file__), "..")
        print(execPath)
        if os.path.isdir(os.path.join(execPath, ".git")):
            updateProcess = QProcess()
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
                pass
            version, url = release.split(" ")
            if __version__ != version:
                updateProcess = QProcess()
                updateProcess.startDetached("powershell.exe", ["powershell", "-Command",
"""
Add-Type -AssemblyName System.IO.Compression.FileSystem
function Unzip {
    param([string]$zipfile, [string]$outpath)
    [System.IO.Compression.ZipFile]::ExtractToDirectory($zipfile, $outpath)
}
$file=New-TemporaryFile
$folder=New-TemporaryFile | %{ rm $_; mkdir $_ }
$path="%s"
Invoke-WebRequest %s -OutFile $file
Unzip file $folder
xcopy $folder/aidoru $path /k /q /y /c /e
%s
""" % (url, execPath)])
                sys.exit(0)
