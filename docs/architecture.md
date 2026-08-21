# Kiến trúc

CLI nạp schema Pydantic nghiêm ngặt, resolve đường dẫn trong sandbox project và chạy validate tổng hợp. Pipeline tạo scene H.264 chuẩn hóa riêng, ghép cut/xfade, sinh và burn ASS, tạo/trộn audio bằng filter graph, chạy loudnorm hai lượt, mã hóa master/preview và ghi JSON report. `input` chỉ đọc; mọi intermediate nằm trong `work`, thành phẩm/log trong `output`.

