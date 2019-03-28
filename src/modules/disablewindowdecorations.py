from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer
from src.Application import Application
from src.modules.module import BaseModule
import os

if os.sys.platform == "win32":
    from PyQt5.QtWinExtras import *
    import struct
    import ctypes
    import ctypes.wintypes as wintypes
    user32 = ctypes.WinDLL('user32')
    user32.GetWindowLongW.restype = wintypes.DWORD
    user32.GetWindowLongW.argtype = [wintypes.HWND, ctypes.c_int]
    user32.SetWindowLongW.restype = wintypes.DWORD
    user32.SetWindowLongW.argtype = [wintypes.HWND, ctypes.c_int, wintypes.DWORD]
    GWL_STYLE = -16

class WindowsModule:

    def __init__(self):
        BaseModule.__init__(self, "nowindecorations", "Disable window decorations (requires restart)")

    def enable(self):
        BaseModule.enable(self)
        Application.mainWindow.nativeEventHandlers.append(self.nativeEventHandler)
        Application.mainWindow.initUIDone.connect(self.initUIDone)

    def disable(self):
        BaseModule.disable(self)

    # events
    def initUIDone(self):
        mainWindow = Application.mainWindow
        mainWindow.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowSystemMenuHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        mainWindow.show()
        hwnd = wintypes.HWND(mainWindow.winId().__int__())
        winprop = user32.GetWindowLongW(hwnd, GWL_STYLE)
        WS_MAXIMIZEBOX=0x00010000
        WS_THICKFRAME=0x00040000
        WS_CAPTION=0x00C00000
        user32.SetWindowLongW(hwnd, GWL_STYLE, winprop | WS_MAXIMIZEBOX | WS_THICKFRAME | WS_CAPTION)
        QtWin.extendFrameIntoClientArea(mainWindow, 1,1,1,1)

    def nativeEventHandler(self, eventType, message):
        if eventType == "windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(message.__int__())
            WM_NCCALCSIZE = 0x0083
            WM_NCHITTEST = 0x0084
            if msg.message == WM_NCCALCSIZE:
                # don't draw titlebars please!
                return True, 0
            elif msg.message == WM_NCHITTEST:
                # LOWORD = x, HIWORD = y
                x, y = struct.unpack('hh', msg.lParam.to_bytes(4, 'little')) # x86 is little endian
                geo = Application.MainWindow.geometry()
                HTLEFT = 10
                HTRIGHT = 11
                HTTOP = 12
                HTTOPLEFT = 13
                HTTOPRIGHT = 14
                HTBOTTOM = 15
                HTBOTTOMLEFT = 16
                HTBOTTOMRIGHT = 17
                BORDER = 3

                vresult = hresult = None
                if geo.left() <= x < geo.left()+BORDER:
                    hresult = HTLEFT
                elif geo.right()-BORDER <= x < geo.right():
                    hresult = HTRIGHT
                if geo.top() <= y < geo.top()+BORDER:
                    vresult = HTTOP
                elif geo.bottom()-BORDER <= y < geo.bottom():
                    vresult = HTBOTTOM

                if hresult == HTLEFT  and vresult == HTTOP:    return True, HTTOPLEFT
                if hresult == HTRIGHT and vresult == HTTOP:    return True, HTTOPRIGHT
                if hresult == HTLEFT  and vresult == HTBOTTOM: return True, HTBOTTOMLEFT
                if hresult == HTRIGHT and vresult == HTBOTTOM: return True, HTBOTTOMRIGHT
                if hresult: return True, hresult
                if vresult: return True, vresult

class LinuxModule:

    def __init__(self):
        BaseModule.__init__(self, "nowindecorations", "Disable window decorations")

    def enable(self):
        BaseModule.enable(self)
        Application.mainWindow.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

    def disable(self):
        BaseModule.disable(self)
        Application.mainWindow.setWindowFlags(Qt.Window)

if os.sys.platform == "win32":
    DisableWindowDecorationsModule = WindowsModule
else:
    DisableWindowDecorationsModule = LinuxModule
