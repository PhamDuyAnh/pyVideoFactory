@echo off
setlocal
cd /d "%~dp0"
set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Links;%PATH%"
if "%~1"=="" (
  echo Cach dung: render_video.bat projects\ten_project [--overwrite]
  exit /b 2
)
if not exist ".venv\Scripts\python.exe" (
  echo Chua co .venv. Hay chay setup_windows.bat truoc.
  exit /b 1
)
".venv\Scripts\python.exe" -m video_factory render %*
exit /b %errorlevel%
