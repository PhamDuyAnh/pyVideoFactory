@echo off
setlocal
cd /d "%~dp0\.."
call render_video.bat projects\example_cq_video %*
