import os

modules = []

# platform specific
## linux
if os.sys.platform == "linux":
    from .mpris import MprisModule
    modules.extend([ MprisModule ])

## macOS
## windows
