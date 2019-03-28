from PyQt5.QtGui import QIcon
from PyQt5.QtWinExtras import *
from PyQt5.QtMultimedia import QMediaPlayer
from src.Application import Application
from src.modules.module import BaseModule

import ctypes
import ctypes.wintypes as wintypes
user32 = ctypes.WinDLL('user32')
user32.RegisterHotKey.restype = wintypes.BOOL
user32.RegisterHotKey.argtype = [wintypes.HWND, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]
user32.UnregisterHotKey.restype = wintypes.BOOL
user32.UnregisterHotKey.argtype = [wintypes.HWND, ctypes.c_int]

WM_HOTKEY = 0x0312
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

class KeyboardShortcutsModule(BaseModule):

    def __init__(self):
        BaseModule.__init__(self, "keyboardshortcuts", "Global keyboard shortcuts")

    def enable(self):
        BaseModule.enable(self)
        mainWindow = Application.mainWindow
        hwnd = wintypes.HWND(mainWindow.winId().__int__())
        user32.RegisterHotKey(hwnd, 0, 0, VK_MEDIA_NEXT_TRACK)
        user32.RegisterHotKey(hwnd, 1, 0, VK_MEDIA_PREV_TRACK)
        user32.RegisterHotKey(hwnd, 2, 0, VK_MEDIA_PLAY_PAUSE)
        self.nativeEventIdx = len(Application.mainWindow.nativeEventHandlers)
        Application.mainWindow.nativeEventHandlers.append(self.nativeEventHandler)

    def disable(self):
        BaseModule.disable(self)
        mainWindow = Application.mainWindow
        hwnd = wintypes.HWND(mainWindow.winId().__int__())
        for i in range(3): user32.UnregisterHotKey(hwnd, i)
        del mainWindow.nativeEventHandlers[self.nativeEventIdx]

    def nativeEventHandler(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            mainWindow = Application.mainWindow
            if msg.message == WM_HOTKEY:
                if   msg.wParam == 0: mainWindow.nextSong()
                elif msg.wParam == 1: mainWindow.prevSong()
                elif msg.wParam == 2: mainWindow.playPause()
