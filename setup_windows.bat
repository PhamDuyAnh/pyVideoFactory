@echo off
setlocal
cd /d "%~dp0"
set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Links;%PATH%"
python --version >nul 2>&1 || (echo Khong tim thay Python. Cai Python 3.11+ tu python.org va bat "Add to PATH". & exit /b 1)
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" || (echo Can Python 3.11 tro len. & exit /b 1)
if not exist ".venv\Scripts\python.exe" python -m venv .venv || exit /b 1
".venv\Scripts\python.exe" -m pip install --upgrade pip || exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt || exit /b 1
".venv\Scripts\python.exe" -m pip install -e . --no-deps || exit /b 1
where ffmpeg >nul 2>&1 || (
  where winget >nul 2>&1 || (echo Khong tim thay winget de cai FFmpeg. & exit /b 1)
  echo Dang cai FFmpeg...
  winget install --id Gyan.FFmpeg --exact --accept-package-agreements --accept-source-agreements || exit /b 1
  set "PATH=%LOCALAPPDATA%\Microsoft\WinGet\Links;%PATH%"
)
where ffmpeg >nul 2>&1 || (echo FFmpeg da cai nhung PATH chua cap nhat. Hay mo terminal moi va chay lai setup_windows.bat. & exit /b 1)
where ffprobe >nul 2>&1 || (echo Khong tim thay ffprobe trong PATH. Hay cai ban FFmpeg day du. & exit /b 1)
".venv\Scripts\python.exe" -c "import video_factory; print('Video Factory', video_factory.__version__)" || exit /b 1
echo Hoan tat. Thu: render_video.bat projects\example_cq_video
