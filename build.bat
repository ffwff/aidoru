@echo off
@rmdir dist /s /q
pyinstaller aidoru.spec || goto :error
powershell -Command "Compress-Archive dist/aidoru aidoru-$ENV:PROCESSOR_ARCHITECTURE.zip"
exit /b 0

:error
exit /b %errorlevel%
