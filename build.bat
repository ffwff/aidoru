@echo off
if "%PROCESSOR_ARCHITECTURE%" == "x86" set ARCH=win32
if "%PROCESSOR_ARCHITECTURE%" == "AMD64" set ARCH=win64
rmdir dist /s /q
set CONSOLE=
pyinstaller aidoru.spec -y || goto :error
powershell -Command "Compress-Archive -Force dist/aidoru aidoru-$ENV:ARCH.zip"
set CONSOLE=1
pyinstaller aidoru.spec -y || goto :error
powershell -Command "Compress-Archive -Force dist/aidoru aidoru-$ENV:ARCH-console.zip"
exit /b 0

:error
exit /b %errorlevel%
