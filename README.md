# XV2DA Video Factory

Công cụ dựng video dọc bằng Python và FFmpeg trên Windows. Pipeline cắt và chuẩn hóa
clip nguồn, ghép cut/crossfade, giữ audio gốc theo từng scene, burn caption tiếng Việt,
trộn hiệu ứng/ambience, chuẩn hóa loudness hai lượt và xuất H.264/AAC.

Công cụ chỉ xử lý tệp cục bộ; không đăng nhập Kling, gọi dịch vụ giọng nói hoặc tải video
lên mạng xã hội.

## Yêu cầu

- Windows 10/11.
- Python 3.11 trở lên.
- WinGet để `setup_windows.bat` có thể tự cài FFmpeg khi máy chưa có.
- Dung lượng trống đủ cho `work/` và các video trong `output/`.

## Cài đặt

Chạy một lần từ Command Prompt hoặc PowerShell tại thư mục repository:

```bat
.\setup_windows.bat
```

Script tạo `.venv`, cài dependencies từ `requirements.txt`, cài package ở editable mode,
kiểm tra `ffmpeg`/`ffprobe`, và tự chạy `winget install Gyan.FFmpeg` nếu FFmpeg còn thiếu.
Nếu FFmpeg vừa được cài nhưng terminal chưa nhận PATH, mở terminal mới và chạy script lại.

Cài thủ công tương đương:

```bat
winget install --id Gyan.FFmpeg --exact --accept-package-agreements --accept-source-agreements
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip install -e . --no-deps
```

## Bắt đầu nhanh

```bat
.\setup_windows.bat
.venv\Scripts\python.exe -m video_factory new-project video_002
.venv\Scripts\python.exe -m video_factory validate projects\video_002
.\render_video.bat projects\video_002 --overwrite
```

Đặt clip trong `projects\video_002\input\video\`, audio trong `input\audio\`, rồi sửa các tên file/thời gian trong `project.yaml`. Master 1080×1920, preview mặc định 540×960, report và `render.log` nằm trong `output\`. File nguồn trong `input\` không bị sửa.

Để giữ tiếng có sẵn trong clip, đặt `source_audio: true` cho scene. Audio được trim theo
`start`/`duration`, đặt đúng vị trí timeline, trộn cùng các track khác và chuẩn hóa về target
LUFS. Scene không khai báo tùy chọn này mặc định không lấy audio nguồn.

```yaml
scenes:
  - id: opening
    file: input/video/scene_01.mp4
    start: 0.4
    duration: 7.6
    source_audio: true
    transition_after: {type: cut, duration: 0.0}
```

Scene và voice ngoài luôn phải nằm trong `project/input`. Font dùng chung được đặt trong
`assets/fonts`; effect/ambience dùng chung có thể đặt trong `assets/audio`. Mọi đường dẫn
asset đều bị giới hạn trong repository.

## Các lệnh chính

Lệnh hữu ích:

```bat
.venv\Scripts\python.exe -m video_factory render projects\video_002 --dry-run
.venv\Scripts\python.exe -m video_factory render projects\video_002 --overwrite
.venv\Scripts\python.exe -m video_factory clean projects\video_002
```

Khi lỗi render, xem `projects\video_002\output\render.log`. Hướng dẫn chi tiết: [cài đặt](docs/installation_windows.md), [quick start](docs/quick_start_vi.md), [cấu hình](docs/project_config_vi.md), [xử lý lỗi](docs/troubleshooting_vi.md).

## Project mẫu

`projects/example_cq_video` dựng năm scene thành video 1080×1920, 24 fps, dài 19,4 giây.
Audio gốc được giữ ở scene 1 và 4; các file WAV ngoài không cần thiết. Cấu hình còn có tone
PTT, pink noise, ticks, caption, cut và crossfade. Xem hướng dẫn riêng tại
[`projects/example_cq_video/README.md`](projects/example_cq_video/README.md).

Output được tạo tại:

```text
projects/example_cq_video/output/final_short_1080p.mp4
projects/example_cq_video/output/preview_960p.mp4
projects/example_cq_video/output/render_report.json
projects/example_cq_video/output/render.log
```

## Phát triển

```bat
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m ruff check .
```

Các thư mục sinh tự động (`work/`, nội dung `output/`, cache và môi trường ảo) không được
commit. File nguồn trong `input/` không bao giờ bị pipeline sửa hoặc ghi đè.
