import os

modules = []

# platform specific
if os.sys.platform == "linux":
    from .mpris import MprisModule
    modules.extend([ MprisModule ])
elif os.sys.platform == "win32":
    from .taskpreview import TaskPreviewModule
    modules.extend([ TaskPreviewModule ])
elif os.sys.platform == "darwin":
    pass
