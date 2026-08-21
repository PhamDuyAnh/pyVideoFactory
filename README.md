# XV2DA Video Factory V1

Công cụ Python cho Windows tự cắt/chuẩn hóa clip Kling, ghép timeline, burn caption tiếng Việt, trộn voice/effect/ambience, chuẩn hóa -14 LUFS và xuất Shorts H.264/AAC. Công cụ không đăng nhập Kling, gọi ElevenLabs hay upload mạng xã hội.

## Bắt đầu nhanh

Yêu cầu Windows 10/11, Python 3.11+ và FFmpeg/ffprobe có trong `PATH`.

```bat
setup_windows.bat
.venv\Scripts\python.exe -m video_factory new-project video_002
.venv\Scripts\python.exe -m video_factory validate projects\video_002
render_video.bat projects\video_002
```

Đặt clip trong `projects\video_002\input\video\`, audio trong `input\audio\`, rồi sửa các tên file/thời gian trong `project.yaml`. Master, preview, report và `render.log` nằm trong `output\`. File nguồn trong `input\` không bị sửa.

Lệnh hữu ích:

```bat
.venv\Scripts\python.exe -m video_factory render projects\video_002 --dry-run
.venv\Scripts\python.exe -m video_factory render projects\video_002 --overwrite
.venv\Scripts\python.exe -m video_factory clean projects\video_002
```

Khi lỗi render, xem `projects\video_002\output\render.log`. Hướng dẫn chi tiết: [cài đặt](docs/installation_windows.md), [quick start](docs/quick_start_vi.md), [cấu hình](docs/project_config_vi.md), [xử lý lỗi](docs/troubleshooting_vi.md).

## Phát triển

```bat
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check .
```

