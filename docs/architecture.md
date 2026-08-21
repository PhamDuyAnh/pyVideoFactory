# Kiến trúc

CLI nạp schema Pydantic nghiêm ngặt và chạy validate tổng hợp. Media người dùng được sandbox trong `project/input`; resolver riêng chỉ cho phép font/effect dùng chung trong `repository/assets` và từ chối traversal khỏi repository. Pipeline tạo scene H.264 chuẩn hóa riêng, ghép cut/xfade, sinh và burn ASS, tạo/trộn audio bằng filter graph, chạy loudnorm hai lượt, mã hóa master/preview và ghi JSON report. `video.width/height` là nguồn kích thước master duy nhất; mọi intermediate nằm trong `work`, thành phẩm/log trong `output`.
