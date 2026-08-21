@echo off
setlocal
cd /d "%~dp0\.."
python --version
ffmpeg -version
ffprobe -version
if exist ".venv\Scripts\python.exe" ".venv\Scripts\python.exe" -m video_factory --help

