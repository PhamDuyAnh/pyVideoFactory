# Cấu hình project.yaml

| Section | Ý nghĩa |
|---|---|
| `project` | ID ASCII, tiêu đề và mô tả metadata |
| `video` | Kích thước, fps, scale `cover`/`contain`, codec, CRF, preset |
| `audio` | 48 kHz stereo, LUFS/true peak và gain mặc định theo role |
| `style` | Font, cỡ/chất màu ASS, viền, vị trí và lề an toàn |
| `scenes` | File, vùng trim và transition `cut`/`crossfade` |
| `captions` | Text và thời gian trên timeline thành phẩm |
| `audio_tracks` | File/tone/noise/ticks/silence, delay, fade, filter radio |
| `outputs` | Đường dẫn master, preview và JSON report |

Đường dẫn phải tương đối với thư mục project. Scene chỉ được đọc từ `input/video`, audio file từ `input/audio`, output phải ở `output`.

```yaml
scenes:
  - id: opening
    file: input/video/scene_01.mp4
    start: 0.4
    duration: 3.0
    transition_after: {type: crossfade, duration: 0.15}
audio_tracks:
  - id: ptt
    type: generated_tone
    role: effect
    start: 0.35
    duration: 0.08
    frequency_hz: 1000
```

Caption Shorts nên tối đa khoảng hai dòng. Giữ `margin_bottom` khoảng 200–300 px ở 1080×1920, lề trái/phải ít nhất 80 px để tránh nút giao diện. Dùng font có glyph tiếng Việt; `font_file: null` cho phép libass tìm font theo `font_name`.

