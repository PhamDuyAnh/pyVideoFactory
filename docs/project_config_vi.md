# Cấu hình project.yaml

| Section | Ý nghĩa |
|---|---|
| `project` | ID ASCII, tiêu đề và mô tả metadata |
| `video` | Nguồn duy nhất cho kích thước master, fps, scale `cover`/`contain`, codec, CRF, preset |
| `audio` | 48 kHz stereo, LUFS/true peak và gain mặc định theo role |
| `style` | Font, cỡ/chất màu ASS, viền, vị trí và lề an toàn |
| `scenes` | File, vùng trim, audio nguồn và transition `cut`/`crossfade` |
| `captions` | Text và thời gian trên timeline thành phẩm |
| `audio_tracks` | File/tone/noise/ticks/silence, delay, fade, filter radio |
| `outputs` | Đường dẫn master, preview 540×960 mặc định và JSON report |

Đường dẫn phải tương đối với thư mục project. Scene chỉ được đọc từ `input/video`; voice chỉ từ `input/audio`; output phải ở `output`. Font được phép ở `repository/assets/fonts`, còn effect/ambience file được phép ở `repository/assets/audio`. Resolver từ chối mọi path thoát khỏi repository hoặc trỏ sang vùng source code.

```yaml
scenes:
  - id: opening
    file: input/video/scene_01.mp4
    start: 0.4
    duration: 3.0
    source_audio: true
    transition_after: {type: crossfade, duration: 0.15}
audio_tracks:
  - id: ptt
    type: generated_tone
    role: effect
    start: 0.35
    duration: 0.08
    frequency_hz: 1000
```

`source_audio` mặc định là `false`. Khi đặt `true`, pipeline đọc audio stream từ chính
file video, trim cùng `start`/`duration`, delay tới vị trí scene trong timeline, rồi trộn
với `audio_tracks` trước khi chạy loudnorm. Với crossfade, audio của hai scene có thể chồng
lên nhau trong khoảng transition.

Caption Shorts nên tối đa khoảng hai dòng. Giữ `margin_bottom` khoảng 200–300 px ở 1080×1920, lề trái/phải ít nhất 80 px để tránh nút giao diện. Ví dụ font dùng chung: `font_file: ../../assets/fonts/NotoSans-Bold.ttf`. Có thể dùng `null` để libass tìm font theo `font_name`.

Với `pixel_format: yuv420p`, `video.width`, `video.height`, `outputs.preview.width` và `outputs.preview.height` đều phải là số chẵn. Không khai báo lại kích thước trong `outputs.master`; master luôn lấy từ `video.width/height`.
