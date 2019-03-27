from PyQt5.QtGui import QIcon
from PyQt5.QtWinExtras import *
from PyQt5.QtMultimedia import QMediaPlayer
from src.Application import Application
from src.modules.module import BaseModule

class TaskPreviewModule(BaseModule):

    def __init__(self):
        BaseModule.__init__(self, "taskpreview", "Taskbar integration")
        
    def enable(self):
        BaseModule.enable(self)
        self.button = QWinTaskbarButton()
        self.button.progress().setPaused(True)
        self.thumbbar = QWinThumbnailToolBar()
        
        self.initThumbbar()
        
        Application.mainWindow.windowShow.connect(self.windowShow)
        Application.mainWindow.media.durationChanged.connect(self.durationChanged)
        Application.mainWindow.media.positionChanged.connect(self.positionChanged)
        Application.mainWindow.media.stateChanged.connect(self.stateChanged)
        
    def disable(self):
        BaseModule.disable(self)
        Application.mainWindow.windowShow.disconnect(self.windowShow)
        Application.mainWindow.media.durationChanged.disconnect(self.durationChanged)
        Application.mainWindow.media.positionChanged.disconnect(self.positionChanged)
        Application.mainWindow.media.stateChanged.disconnect(self.stateChanged)
        del self.button
        del self.thumbbar
    
    # thumbbar
    def initThumbbar(self):
        prev = QWinThumbnailToolButton(self.thumbbar)
        prev.setIcon(QIcon("icons/media-skip-backward"))
        self.thumbbar.addButton(prev)
        
        self.playPause = playPause = QWinThumbnailToolButton(self.thumbbar)
        playPause.setIcon(QIcon("icons/media-playback-start"))
        self.thumbbar.addButton(playPause)
        
        next = QWinThumbnailToolButton(self.thumbbar)
        next.setIcon(QIcon("icons/media-skip-forward"))
        self.thumbbar.addButton(next)
        
        prev.clicked.connect(Application.mainWindow.prevSong)
        next.clicked.connect(Application.mainWindow.nextSong)
        playPause.clicked.connect(Application.mainWindow.playPause)
    
    # events
    def windowShow(self):
        self.button.setWindow(Application.mainWindow.windowHandle())
        self.thumbbar.setWindow(Application.mainWindow.windowHandle())
        
    def durationChanged(self, duration):
        self.button.progress().show()
        self.button.progress().setMaximum(duration)
        
    def positionChanged(self, position):
        self.button.progress().setValue(position)
    
    def stateChanged(self, state):
        self.button.progress().setPaused(state != QMediaPlayer.PlayingState)
        if state == QMediaPlayer.PlayingState:
            self.playPause.setIcon(QIcon("icons/media-playback-pause"))
        else:
            self.playPause.setIcon(QIcon("icons/media-playback-start"))