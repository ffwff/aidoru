import os

modules = []

# xplatform
from .disablewindowdecorations import DisableWindowDecorationsModule
modules.extend([ DisableWindowDecorationsModule ])

# platform specific
if os.sys.platform == "linux":

    try:
        from .mpris import MprisModule
        modules.append(MprisModule)
    except ImportError:
        print("can't import mpris module! is dbus-python installed?")

elif os.sys.platform == "win32":

    from .taskpreview import TaskPreviewModule
    from .keyboardshortcuts import KeyboardShortcutsModule
    modules.extend([
        TaskPreviewModule,
        KeyboardShortcutsModule
    ])

elif os.sys.platform == "darwin":
    pass
