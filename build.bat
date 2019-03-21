@echo off
if "%PROCESSOR_ARCHITECTURE%" == "x86" set ARCH=win32
if "%PROCESSOR_ARCHITECTURE%" == "AMD64" set ARCH=win64
rmdir dist /s /q
pyinstaller aidoru.spec || goto :error
powershell -Command "Compress-Archive -Force dist/aidoru aidoru-$ENV:ARCH.zip"
pyinstaller aidoru-console.spec || goto :error
powershell -Command "Compress-Archive -Force dist/aidoru aidoru-$ENV:ARCH-console.zip"
exit /b 0

:error
exit /b %errorlevel%
