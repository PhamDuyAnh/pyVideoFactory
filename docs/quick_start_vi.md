# Quick start (10–15 phút)

1. Xuất các clip Kling thành MP4; nên để dư vài frame ở đầu/cuối vùng cần dùng.
2. Chạy `setup_windows.bat`, rồi tạo project: `.venv\Scripts\python.exe -m video_factory new-project video_002`.
3. Đổi tên clip `scene_01.mp4`, `scene_02.mp4`… và copy vào `projects\video_002\input\video\`. Copy voice WAV/MP3 vào `input\audio\`.
4. Mở `project.yaml`: sửa `title`, danh sách `scenes`, `start`, `duration`, caption và audio. Mọi thời gian dùng giây.
5. Chạy `validate projects\video_002`. Sửa toàn bộ dòng `LOI`; dòng `CANH BAO` về fps/resolution thường được pipeline tự chuẩn hóa.
6. Xem kế hoạch không tạo video bằng `python -m video_factory render projects\video_002 --dry-run` (dùng Python trong `.venv`).
7. Render bằng `render_video.bat projects\video_002`.
8. Xem master, preview và report trong `projects\video_002\output\`. Nếu thất bại, mở `render.log`.

