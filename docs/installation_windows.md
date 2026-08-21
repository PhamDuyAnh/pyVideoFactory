# Cài đặt trên Windows

1. Cài Python 3.11+ từ python.org và bật **Add Python to PATH**.
2. Cài bản FFmpeg đầy đủ có libass, ví dụ `winget install Gyan.FFmpeg`.
3. Đóng/mở terminal để cập nhật PATH; kiểm tra `ffmpeg -version` và `ffprobe -version`.
4. Trong repo chạy `setup_windows.bat`. Script tạo `.venv`, cài dependency, kiểm tra công cụ và import.

Script không tải hay chạy binary FFmpeg từ Internet. Nếu tổ chức chặn `winget`, hãy cài FFmpeg theo chính sách nội bộ rồi thêm thư mục `bin` vào PATH.

