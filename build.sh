#!/bin/sh
source ./venv/bin/activate
rm -rf dist
pyinstaller aidoru.spec || exit $@
cd dist && zip -r -9 "../aidoru-$(uname -s)-$(uname -m).zip" aidoru
