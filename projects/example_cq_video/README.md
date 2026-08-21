# Example CQ Video

Project mẫu dựng video CQ dọc từ năm clip nguồn. Phiên bản hiện tại dài 19,4 giây, giữ
audio nhúng trong scene 1 và scene 4, không dùng file WAV ngoài.

## Input

Đặt các file sau vào đúng chỗ:

```text
input/video/scene_01.mp4 ... scene_05.mp4
```

Input không bao giờ bị công cụ sửa hoặc ghi đè.

## Hiệu ứng và timeline

- Scene 1 lấy từ giây 0,4, dài 7,6 giây và giữ audio gốc.
- Scene 4 lấy từ giây 0,2, dài 3,3 giây và giữ audio gốc.
- Timeline sử dụng cut và crossfade 0,15 giây.
- Audio bổ sung gồm tone PTT, pink noise và ticks được sinh bằng FFmpeg.
- Caption được burn trực tiếp; font `Noto Sans` dùng qua font hệ thống.
- Master 1080×1920/24 fps; preview 540×960.

## Kiểm tra và render

Từ thư mục gốc repository:

```bat
setup_windows.bat
.venv\Scripts\python.exe -m video_factory validate projects\example_cq_video
render_video.bat projects\example_cq_video --overwrite
```

Kết quả nằm trong `output/`. Kiểm tra `render_report.json` để đối chiếu
`expected_duration` và `actual_duration`; xem `render.log` nếu FFmpeg báo lỗi.
