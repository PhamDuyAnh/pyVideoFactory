# Xử lý sự cố

- **Không thấy Python:** cài Python 3.11+, bật Add to PATH, mở terminal mới.
- **Không thấy FFmpeg/ffprobe:** cài bản đầy đủ, thêm `bin` vào PATH rồi chạy `scripts\check_environment.bat`.
- **Thiếu subtitles/libass:** thay bằng build FFmpeg đầy đủ; `validate` sẽ báo filter thiếu.
- **Sai font tiếng Việt:** dùng font hỗ trợ tiếng Việt, đặt trong `assets/fonts`, cấu hình `font_file`/`font_name` đúng.
- **Clip thiếu audio:** bình thường khi `source_audio: false`; pipeline tạo audio thành phẩm từ tracks hoặc silence.
- **Sai resolution/fps:** đây thường là cảnh báo; pipeline scale/crop và đổi fps. Chọn `contain` nếu không muốn crop.
- **Trim vượt duration:** giảm `start`/`duration` theo số liệu validate.
- **Output đã tồn tại:** kiểm tra file cũ rồi thêm `--overwrite`; mặc định công cụ bảo vệ output.
- **Path có khoảng trắng:** YAML vẫn dùng chuỗi bình thường; lệnh FFmpeg dùng argument list an toàn.
- **Antivirus cảnh báo BAT:** đọc nội dung BAT; script chỉ tạo venv, pip install và gọi Python/FFmpeg, không tải binary.
- **Render chậm:** dùng `preset: fast`/`veryfast` khi thử; `medium` cho bản cuối. File trung gian giúp xác định stage chậm.
- **Render thất bại:** mở `output/render.log`, tìm stage cuối và command đầy đủ.

