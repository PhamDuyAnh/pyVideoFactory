@echo off
setlocal
cd /d "%~dp0"
python --version >nul 2>&1 || (echo Khong tim thay Python. Cai Python 3.11+ tu python.org va bat "Add to PATH". & exit /b 1)
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3,11) else 1)" || (echo Can Python 3.11 tro len. & exit /b 1)
if not exist ".venv\Scripts\python.exe" python -m venv .venv || exit /b 1
".venv\Scripts\python.exe" -m pip install --upgrade pip || exit /b 1
".venv\Scripts\python.exe" -m pip install -r requirements.txt || exit /b 1
".venv\Scripts\python.exe" -m pip install -e . --no-deps || exit /b 1
where ffmpeg >nul 2>&1 || (echo Khong tim thay FFmpeg. Cai bang: winget install Gyan.FFmpeg, mo terminal moi va chay lai. & exit /b 1)
where ffprobe >nul 2>&1 || (echo Khong tim thay ffprobe trong PATH. Hay cai ban FFmpeg day du. & exit /b 1)
".venv\Scripts\python.exe" -c "import video_factory; print('Video Factory', video_factory.__version__)" || exit /b 1
echo Hoan tat. Thu: render_video.bat projects\example_cq_video
