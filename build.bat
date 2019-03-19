@echo off
rmdir dist /s /q
pyinstaller aidoru.spec || goto :error
if "%PROCESSOR_ARCHITECTURE%" == "x86" set ARCH=win32
if "%PROCESSOR_ARCHITECTURE%" == "AMD64" set ARCH=win64
powershell -Command "Compress-Archive dist/aidoru aidoru-$ENV:ARCH.zip"
exit /b 0

:error
exit /b %errorlevel%
