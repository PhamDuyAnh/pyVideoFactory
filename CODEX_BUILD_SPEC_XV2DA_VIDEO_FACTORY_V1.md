# CODEX BUILD SPEC — XV2DA Video Factory V1 for Windows

## 0. Vai trò và cách làm việc

Bạn là Codex đang làm việc trực tiếp trong thư mục gốc của repository `pyVideoFactory` trên Windows.

Hãy đọc toàn bộ tài liệu này trước khi thay đổi file. Sau đó:

1. Khảo sát repository và giữ nguyên mọi file/ thay đổi không liên quan của người dùng.
2. Nếu có `AGENTS.md`, phải đọc và tuân thủ trước khi triển khai.
3. Lập kế hoạch ngắn rồi triển khai trọn vẹn V1; không chỉ viết mẫu minh họa.
4. Chỉ hỏi người dùng khi có lựa chọn ảnh hưởng lớn mà tài liệu này chưa quyết định được.
5. Ưu tiên giải pháp đơn giản, ổn định, dễ kiểm tra và phù hợp người mới dùng Python.
6. Sau mỗi nhóm thay đổi lớn, chạy kiểm thử phù hợp.
7. Không tự `git commit`, `git push`, tạo release hoặc đồng bộ GitHub.
8. Không ghi API key, mật khẩu, token hoặc dữ liệu riêng tư vào repository.

Ngôn ngữ:

- Source code, tên biến và docstring: tiếng Anh.
- Hướng dẫn cho người dùng, thông báo CLI và README: ưu tiên tiếng Việt rõ ràng.
- Tên file và thư mục: ASCII, chữ thường, `snake_case` hoặc `kebab-case`; không dùng khoảng trắng.

---

## 1. Mục tiêu sản phẩm

Xây dựng **XV2DA Video Factory V1**, một công cụ Python chạy trên Windows để tự động dựng video dọc ngắn từ các clip tạo bởi Kling.

Quy trình mong muốn:

1. GPT chuẩn bị kịch bản, timeline, phụ đề và hướng dẫn tạo clip.
2. Người dùng tạo các clip riêng lẻ bằng Kling và tải về.
3. Giọng nói được tạo độc lập bằng ElevenLabs hoặc thu âm thủ công; V1 không bắt buộc gọi ElevenLabs API.
4. Người dùng đặt clip/audio vào đúng thư mục của project video.
5. Người dùng nhấp đúp `render_video.bat` hoặc chạy một lệnh Python.
6. Video Factory tự kiểm tra, cắt, ghép, chèn phụ đề, tạo/trộn hiệu ứng âm thanh và xuất video Shorts hoàn chỉnh.

Đối tượng sử dụng là người mới dựng video. Không yêu cầu họ thao tác timeline bằng Kdenlive, CapCut hoặc Premiere.

### Mục tiêu V1

- Windows 10/11.
- Python 3.11 trở lên.
- FFmpeg/ffprobe.
- Video dọc 1080 × 1920.
- H.264 + AAC, `.mp4`.
- 24 hoặc 30 fps, mặc định 24 fps.
- Cấu hình project bằng YAML.
- Hỗ trợ nhiều project video độc lập trong cùng repository.
- Cắt từng clip theo `start` và `duration`.
- Chuẩn hóa kích thước, frame rate, pixel format và audio.
- Ghép clip theo thứ tự.
- Chèn caption/subtitle có thời gian định trước.
- Trộn voice, sound effect và ambience.
- Tự tạo một số hiệu ứng cơ bản bằng FFmpeg: radio static, PTT beep và clock ticks.
- Chuẩn hóa âm lượng đầu ra ở mức hợp lý cho video mạng xã hội.
- Xuất bản chính 1080p và bản preview 720p.
- Có `validate`, `render`, `clean` và `new-project`.
- Có log dễ hiểu và báo lỗi có hướng dẫn khắc phục.
- Có test tự động không phụ thuộc clip thật của người dùng.

### Không thuộc V1

- Không tự đăng nhập hoặc tự thao tác Kling.
- Không tự upload lên YouTube/Facebook/TikTok.
- Không clone giọng nói.
- Không bắt buộc dùng ElevenLabs API.
- Không làm GUI desktop.
- Không làm trình biên tập timeline tương tác.
- Không dùng moviepy nếu FFmpeg trực tiếp giải quyết ổn định hơn.
- Không thêm database, web server, Docker hoặc cloud service.

---

## 2. Kiến trúc và cấu trúc repository

Tạo cấu trúc mục tiêu sau. Có thể điều chỉnh nhỏ nếu repository hiện hữu đã có convention tốt hơn, nhưng phải giữ ranh giới rõ giữa source code, tài nguyên dùng chung và từng project video.

```text
pyVideoFactory/
├─ README.md
├─ CHANGELOG.md
├─ LICENSE                         # chỉ tạo nếu người dùng đã chọn license; nếu chưa thì bỏ qua
├─ pyproject.toml
├─ requirements.txt
├─ requirements-dev.txt
├─ .gitignore
├─ .env.example
├─ render_video.bat
├─ setup_windows.bat
├─ scripts/
│  ├─ check_environment.bat
│  └─ render_example.bat
├─ src/
│  └─ video_factory/
│     ├─ __init__.py
│     ├─ __main__.py
│     ├─ cli.py
│     ├─ config.py
│     ├─ models.py
│     ├─ paths.py
│     ├─ ffmpeg.py
│     ├─ probe.py
│     ├─ validate.py
│     ├─ timeline.py
│     ├─ subtitles.py
│     ├─ audio.py
│     ├─ render.py
│     ├─ project.py
│     ├─ logging_utils.py
│     └─ exceptions.py
├─ assets/
│  ├─ audio/
│  │  ├─ README.md
│  │  ├─ ambience/
│  │  └─ effects/
│  ├─ fonts/
│  │  └─ README.md
│  └─ templates/
│     ├─ project.yaml
│     └─ subtitles.ass.j2
├─ projects/
│  ├─ README.md
│  └─ example_cq_video/
│     ├─ project.yaml
│     ├─ input/
│     │  ├─ video/
│     │  │  └─ README.md
│     │  └─ audio/
│     │     └─ README.md
│     ├─ work/
│     │  └─ .gitkeep
│     ├─ output/
│     │  └─ .gitkeep
│     └─ README.md
├─ tests/
│  ├─ conftest.py
│  ├─ test_config.py
│  ├─ test_probe.py
│  ├─ test_timeline.py
│  ├─ test_subtitles.py
│  ├─ test_validate.py
│  └─ test_smoke_render.py
└─ docs/
   ├─ installation_windows.md
   ├─ quick_start_vi.md
   ├─ project_config_vi.md
   ├─ troubleshooting_vi.md
   └─ architecture.md
```

### Quy tắc dữ liệu project

- `input/`: tài nguyên do người dùng cung cấp, tuyệt đối không sửa/ghi đè.
- `work/`: file trung gian có thể xóa và tạo lại.
- `output/`: video thành phẩm, preview, report và log riêng của project.
- `assets/`: tài nguyên dùng chung cho mọi video.
- Source code không được phụ thuộc tên `XV2DA` cứng; XV2DA chỉ xuất hiện trong project mẫu/cấu hình.
- Đường dẫn trong YAML phải tương đối so với thư mục project, không phụ thuộc ổ đĩa của người dùng.
- Tất cả thư mục build, video/audio đầu vào dung lượng lớn và output phải được `.gitignore` hợp lý.
- Giữ các file `.gitkeep` và README để cấu trúc thư mục tồn tại trên GitHub.

---

## 3. Trải nghiệm sử dụng bắt buộc

### Cài đặt lần đầu

Người dùng mở PowerShell hoặc Command Prompt trong repo và chạy:

```bat
setup_windows.bat
```

Script phải:

1. Kiểm tra Python có tồn tại và phiên bản >= 3.11.
2. Tạo `.venv` nếu chưa có.
3. Cài dependencies.
4. Kiểm tra `ffmpeg` và `ffprobe` trong `PATH`.
5. Nếu thiếu FFmpeg, dừng an toàn và in hướng dẫn cài đặt rõ ràng; không tự tải hoặc chạy binary từ Internet.
6. Chạy một kiểm tra import ngắn.
7. In lệnh tiếp theo cho người dùng.

### Tạo project mới

```bat
.venv\Scripts\python.exe -m video_factory new-project video_002
```

Kết quả:

- Tạo `projects/video_002/` từ template.
- Không ghi đè nếu project đã tồn tại.
- Tạo `project.yaml`, các thư mục input/work/output và README ngắn.

### Kiểm tra project

```bat
.venv\Scripts\python.exe -m video_factory validate projects\video_002
```

Lệnh phải kiểm tra tối thiểu:

- YAML hợp lệ và đúng schema.
- Mọi file được tham chiếu đều tồn tại.
- Clip có video stream.
- Audio có audio stream.
- `start >= 0`, `duration > 0`.
- `start + duration` không vượt quá clip nguồn, cho phép sai số nhỏ.
- Caption không vượt quá thời lượng thành phẩm.
- ID scene/audio/caption không trùng.
- Resolution/fps/codec nguồn chỉ cảnh báo nếu có thể tự chuẩn hóa.
- FFmpeg có các filter cần thiết (`subtitles`/`ass`, `loudnorm`, `amix`, `scale`, `fps`).
- Font cấu hình tồn tại hoặc có fallback an toàn.
- Ước tính timeline cuối cùng và in bảng cảnh.

### Render

Cách dễ nhất:

```bat
render_video.bat projects\example_cq_video
```

Hoặc:

```bat
.venv\Scripts\python.exe -m video_factory render projects\example_cq_video
```

Yêu cầu:

- Mặc định chạy validate trước.
- Không ghi đè file thành phẩm nếu chưa có `--overwrite`; có thể tạo tên có timestamp hoặc trả lỗi rõ ràng.
- Hiển thị tiến độ theo stage, không in toàn bộ log FFmpeg gây rối.
- Lưu full FFmpeg command/log vào `output/render.log`.
- Nếu render thất bại, giữ log và in nguyên nhân/đường dẫn log.
- Khi thành công, in đường dẫn tuyệt đối tới master, preview và report.

### Clean

```bat
.venv\Scripts\python.exe -m video_factory clean projects\example_cq_video
```

- Chỉ xóa nội dung trong `work/`.
- Không xóa `input/` hoặc `output/`.
- Có `--include-output` nhưng phải yêu cầu xác nhận tương tác, trừ khi đồng thời có `--yes`.

### Dry-run

```bat
.venv\Scripts\python.exe -m video_factory render projects\example_cq_video --dry-run
```

- Validate đầy đủ.
- In timeline, file đầu vào, hiệu ứng, caption và lệnh dự kiến.
- Không tạo video.

---

## 4. Định dạng `project.yaml`

Dùng YAML và xác thực bằng Pydantic. Tạo template được comment rõ ràng. Schema tối thiểu:

```yaml
schema_version: 1

project:
  id: example_cq_video
  title: "XV2DA calls CQ in despair"
  description: "Video HAM vui: gọi CQ nhưng không ai trả lời."

video:
  width: 1080
  height: 1920
  fps: 24
  background_color: "#000000"
  video_codec: libx264
  pixel_format: yuv420p
  crf: 19
  preset: medium

audio:
  sample_rate: 48000
  channels: 2
  target_lufs: -14.0
  true_peak_db: -1.5
  default_voice_gain_db: 0.0
  default_effect_gain_db: -12.0
  default_ambience_gain_db: -24.0

style:
  font_file: "../../assets/fonts/NotoSans-Bold.ttf"
  font_name: "Noto Sans"
  font_size: 66
  primary_color: "#FFFFFF"
  outline_color: "#000000"
  outline_width: 4
  shadow: 1
  alignment: bottom_center
  margin_left: 80
  margin_right: 80
  margin_bottom: 250

scenes:
  - id: first_cq
    file: input/video/scene_01.mp4
    start: 0.40
    duration: 5.10
    transition_after:
      type: cut
      duration: 0.0

  - id: listening
    file: input/video/scene_02.mp4
    start: 0.50
    duration: 2.00
    transition_after:
      type: crossfade
      duration: 0.15

captions:
  - id: opening_caption
    text: "Tối nay nhất định có DX!"
    start: 0.20
    end: 2.20
    position: bottom_center

audio_tracks:
  - id: first_cq_voice
    type: file
    file: input/audio/cq_first.wav
    start: 0.60
    trim_start: 0.0
    gain_db: 0.0
    fade_in: 0.03
    fade_out: 0.08

  - id: ptt_start
    type: generated_tone
    start: 0.42
    duration: 0.08
    frequency_hz: 1000
    gain_db: -16.0

  - id: listening_static
    type: generated_noise
    noise: pink
    start: 5.70
    duration: 1.60
    highpass_hz: 350
    lowpass_hz: 3200
    gain_db: -24.0

  - id: clock_ticks
    type: generated_ticks
    start: 7.80
    duration: 2.20
    interval: 0.16
    frequency_hz: 1800
    gain_db: -20.0

outputs:
  master:
    file: output/final_short_1080p.mp4
    width: 1080
    height: 1920
  preview:
    enabled: true
    file: output/preview_720p.mp4
    width: 405
    height: 720
    crf: 25
  report:
    file: output/render_report.json
```

### Quy tắc schema

- Dùng seconds dạng số thực.
- Timeline caption/audio tính trên video thành phẩm sau khi đã xử lý transition.
- V1 hỗ trợ transition `cut` và `crossfade`; nếu crossfade làm kiến trúc phức tạp, vẫn phải hỗ trợ ít nhất `cut`, đồng thời validate và báo rõ `crossfade` chưa hỗ trợ. Tuy nhiên ưu tiên triển khai được cả hai.
- Audio type V1: `file`, `generated_tone`, `generated_noise`, `generated_ticks`, `silence`.
- Cho phép track `role`: `voice`, `effect`, `ambience` để áp default gain.
- Mọi field không biết phải bị báo lỗi, tránh gõ sai mà bị bỏ qua âm thầm.
- Error phải chỉ rõ đường dẫn field, ví dụ `scenes[2].duration`.

---

## 5. Pipeline render

Ưu tiên pipeline nhiều stage dễ debug thay vì một filter graph khổng lồ khó bảo trì.

### Stage 1 — Probe và validate

- Chạy `ffprobe` JSON.
- Thu thập duration, stream, resolution, fps, codec, sample rate và channel layout.
- Tạo bảng summary.

### Stage 2 — Chuẩn hóa từng scene

Mỗi scene tạo một file trung gian trong `work/scenes/`:

- Seek/cắt chính xác.
- Scale theo kiểu `cover` hoặc `contain`; mặc định `cover` nhưng không làm méo tỷ lệ.
- Nếu cover: scale rồi crop giữa.
- FPS đồng nhất.
- SAR = 1.
- `yuv420p`.
- Tạo silent audio nếu clip không có audio.
- Audio nguồn của Kling mặc định tắt (`source_audio: false`) trừ khi YAML bật rõ.
- Dùng codec trung gian hợp lý hoặc H.264 chất lượng cao; ưu tiên ổn định và dung lượng vừa phải.

### Stage 3 — Ghép timeline video

- Ghép theo thứ tự.
- Hỗ trợ cut chắc chắn.
- Nếu hỗ trợ crossfade, tính offset đúng sau khi trừ thời lượng overlap.
- Tạo `timeline.json` trong `work/` để debug.

### Stage 4 — Subtitle/caption

- Sinh file ASS trong `work/subtitles.ass`.
- Dùng font chỉ định và libass để hỗ trợ tiếng Việt.
- Escape đúng dấu nháy, dấu `:`, ký tự Unicode và xuống dòng.
- Có safe area cho giao diện YouTube Shorts: không đặt chữ quá sát trên, dưới hoặc mép phải.
- Caption phải dễ đọc trên điện thoại: viền đen, tối đa khoảng 2 dòng; validate cảnh báo nếu quá dài.
- Burn subtitle vào video; không chỉ tạo subtitle stream rời.

### Stage 5 — Audio

- Tất cả audio được chuyển về 48 kHz stereo floating point trong filter graph.
- Delay từng track đến đúng `start`.
- Trim và fade từng track.
- File voice không bị radio-filter mặc định.
- Cho phép tùy chọn `radio_voice` với high-pass, low-pass và compression nhẹ cho các câu phát qua máy.
- Trộn bằng `amix`, tránh clipping.
- Áp loudness normalization ở bước cuối, mục tiêu mặc định -14 LUFS, true peak <= -1.5 dBTP.
- Nếu loudnorm two-pass quá phức tạp, triển khai two-pass ở cấp pipeline; không giả vờ đã normalize khi chỉ giảm gain.
- Nếu không có audio track nào, tạo silent AAC để output tương thích mạng xã hội.

### Stage 6 — Master và preview

Master:

- MP4 faststart.
- H.264 `libx264`, CRF/preset từ YAML.
- AAC 48 kHz stereo, khoảng 192 kbps.
- `yuv420p`.
- Resolution đúng.
- Metadata title/comment tùy chọn.

Preview:

- 405 × 720 hoặc cấu hình YAML.
- Giữ tỷ lệ 9:16.
- CRF cao hơn để file nhỏ.
- Không làm ảnh hưởng master.

### Stage 7 — Report

Tạo `render_report.json` gồm:

- Version ứng dụng.
- Thời điểm render.
- Python/FFmpeg version.
- Hash hoặc size/mtime của file input.
- Timeline scene.
- Duration dự kiến và duration thực tế.
- Thông số master/preview.
- Warning.
- Thời gian render từng stage.
- Kết quả thành công/thất bại.

---

## 6. Thiết kế source code

### Yêu cầu chung

- Dùng `pathlib.Path`, không nối đường dẫn bằng chuỗi.
- Dùng `subprocess.run` với argument list, không dùng `shell=True` cho lệnh FFmpeg.
- Đặt timeout hợp lý cho probe; render có thể không đặt timeout cứng hoặc cấu hình được.
- Log command ở dạng đã quote để debug, nhưng không thực thi command qua shell.
- Exception riêng: configuration, validation, FFmpeg missing, probe failure, render failure.
- CLI trả exit code khác 0 khi lỗi.
- Không `except Exception: pass`.
- Không in traceback cho người dùng thông thường; hỗ trợ `--debug` để hiện traceback.
- Tách pure logic (timeline/config) khỏi thao tác subprocess để test dễ.
- Có type hints đầy đủ cho public functions.
- Dùng `ruff` và `pytest`; có thể dùng `mypy` nếu không làm V1 quá nặng.

### Dependencies đề xuất

Runtime tối thiểu:

- `pydantic>=2`
- `PyYAML`
- `typer` hoặc `argparse`; ưu tiên `typer` nếu giúp CLI rõ ràng nhưng không bắt buộc.
- `rich` cho bảng/progress/log thân thiện.
- `jinja2` nếu dùng template ASS.

Dev:

- `pytest`
- `pytest-cov`
- `ruff`

Không thêm dependency nếu standard library đã đủ và giải pháp vẫn rõ ràng.

---

## 7. Tài nguyên âm thanh và bản quyền

- Không tải hoặc nhúng file âm thanh có bản quyền không rõ nguồn gốc.
- Các hiệu ứng tone/noise/tick nên được tổng hợp bằng FFmpeg.
- Nếu cần audio mẫu, tạo bằng code hoặc chỉ để placeholder README.
- Không commit giọng clone, giọng thật của người dùng hoặc ElevenLabs API key.
- `.env.example` có thể chứa:

```dotenv
# Optional, not required for V1 rendering
ELEVENLABS_API_KEY=
```

- V1 không được thất bại chỉ vì không có `.env` hoặc API key.

---

## 8. Project mẫu `example_cq_video`

Tạo project mẫu dùng để minh họa workflow XV2DA, nhưng không commit clip/audio thật dung lượng lớn.

README project mẫu phải hướng dẫn tên file mong đợi:

```text
input/video/scene_01.mp4
input/video/scene_02.mp4
input/video/scene_03.mp4
input/video/scene_04.mp4
input/video/scene_05.mp4

input/audio/cq_first.wav
input/audio/cq_tired.wav
input/audio/mosquito.wav       # tùy chọn
```

Timeline mục tiêu khoảng 18 giây:

1. First CQ: khoảng 5.1 giây.
2. Listening/static: khoảng 2 giây.
3. Time passing: khoảng 2.8 giây.
4. Second CQ: khoảng 3.3 giây.
5. Punchline: khoảng 4 giây.

Caption mẫu:

- `Tối nay nhất định có DX!`
- `Hơn một giờ sau…`
- `Có ai nghe XV2DA không?`

Không bắt buộc project mẫu render được khi clone repository vì không có media thật. `validate` phải báo file nào còn thiếu một cách thân thiện.

---

## 9. Testing bắt buộc

### Unit tests

- Load YAML hợp lệ.
- Báo field lạ/field thiếu.
- Resolve đường dẫn project an toàn.
- Tính duration với cut.
- Tính duration/offset với crossfade nếu đã hỗ trợ.
- Caption ngoài timeline bị báo lỗi.
- Scene trim vượt source duration bị báo.
- Escape subtitle tiếng Việt đúng.
- FFprobe JSON parse đúng.
- Command argument được xây đúng trên Windows.

### Smoke render

Test phải tự tạo media ngắn bằng FFmpeg trong temporary directory:

- 2–3 color clips dọc hoặc kích thước nhỏ để test nhanh.
- Tone hoặc silent audio.
- Một caption tiếng Việt có dấu.
- Render video thành phẩm vài giây.
- Probe output và assert:
  - Có video + audio.
  - Resolution/fps đúng cấu hình test.
  - Duration trong sai số cho phép.
  - Pixel format tương thích.

Nếu máy CI/dev không có FFmpeg, smoke test được `skip` với lý do rõ ràng; unit test khác vẫn phải chạy.

### Lệnh chất lượng

Các lệnh sau phải chạy được từ repo root:

```bat
.venv\Scripts\python.exe -m pytest
.venv\Scripts\python.exe -m ruff check .
.venv\Scripts\python.exe -m video_factory --help
```

---

## 10. README và tài liệu

### `README.md`

Phải trả lời nhanh:

1. Công cụ này làm gì?
2. Cần cài gì?
3. Setup lần đầu thế nào?
4. Tạo project mới thế nào?
5. Đặt clip/audio ở đâu?
6. Render bằng một cú nhấp/lệnh nào?
7. Output nằm ở đâu?
8. Cách xem log khi lỗi.

### `docs/quick_start_vi.md`

Viết cho người mới, tối đa khoảng 10–15 phút thao tác:

- Chuẩn bị clip Kling.
- Đặt tên file.
- Copy vào project.
- Chỉnh vài giá trị YAML cơ bản.
- Validate.
- Render.
- Xem output.

### `docs/project_config_vi.md`

Giải thích từng section YAML bằng bảng, có ví dụ ngắn và lưu ý safe area của Shorts.

### `docs/troubleshooting_vi.md`

Tối thiểu gồm:

- Không tìm thấy Python.
- Không tìm thấy FFmpeg/ffprobe.
- FFmpeg thiếu filter subtitles/libass.
- Font tiếng Việt không hiển thị.
- File clip thiếu audio.
- Clip sai resolution/fps.
- Trim vượt thời lượng.
- Output bị ghi đè.
- Windows path có khoảng trắng.
- Antivirus cảnh báo file BAT.
- Render chậm.

---

## 11. `.gitignore`

Bỏ qua tối thiểu:

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
.env

projects/*/input/video/*
projects/*/input/audio/*
projects/*/work/*
projects/*/output/*

!projects/*/input/video/README.md
!projects/*/input/audio/README.md
!projects/*/work/.gitkeep
!projects/*/output/.gitkeep

*.mp4
*.mov
*.mkv
*.wav
*.mp3
*.flac
```

Kiểm tra cẩn thận để template hoặc test fixture cần thiết không bị ignore ngoài ý muốn.

---

## 12. Tiêu chí nghiệm thu V1

V1 được xem là hoàn thành khi:

1. Setup trên Windows được mô tả rõ và batch scripts không chứa đường dẫn tuyệt đối theo máy tác giả.
2. `python -m video_factory --help` hoạt động.
3. Có thể tạo project mới.
4. `validate` báo đầy đủ file thiếu/lỗi cấu hình trong một lần, không bắt người dùng sửa từng lỗi rồi chạy lại mới thấy lỗi tiếp.
5. Smoke test tạo được MP4 có hình, tiếng và caption tiếng Việt.
6. Với media thật, `render` tạo được master 1080 × 1920 và preview 720p.
7. Timeline cuối đúng trong sai số 1 frame hoặc sai số hợp lý được ghi rõ.
8. Input không bị sửa hoặc ghi đè.
9. Không có secret hoặc media cá nhân trong Git.
10. `pytest` và `ruff check` vượt qua.
11. README đủ để một người mới thực hiện lại mà không cần đọc source code.
12. Codex báo lại chính xác file đã tạo/sửa, lệnh đã test, kết quả và giới hạn còn lại.

---

## 13. Trình tự triển khai đề xuất cho Codex

Thực hiện theo thứ tự:

1. Inspect repo và đọc instruction hiện hữu.
2. Tạo package skeleton và `pyproject.toml`.
3. Triển khai models/config/path/probe.
4. Triển khai validate và CLI.
5. Triển khai scene normalization + concat cut.
6. Triển khai ASS subtitle generation/burn-in.
7. Triển khai audio file/tone/noise/ticks + mixing.
8. Triển khai loudness normalization.
9. Triển khai master/preview/report.
10. Tạo batch scripts Windows.
11. Tạo project/template mẫu.
12. Viết unit tests và smoke render.
13. Viết README/docs.
14. Chạy format/lint/test/smoke.
15. Thử `--help`, `new-project`, `validate`, `render --dry-run`.
16. Review `.gitignore` và `git diff` để chắc chắn không đưa media/secret vào Git.
17. Báo cáo bàn giao; không commit/push.

---

## 14. Cách phản hồi sau khi hoàn thành

Phản hồi cuối cùng bằng tiếng Việt, ngắn gọn nhưng có bằng chứng:

- Kết quả V1 đã làm được.
- Các file/nhóm file chính.
- Lệnh setup và render đầu tiên.
- Test/lint đã chạy và kết quả.
- Điều gì chưa thuộc V1.
- Bước thực tế tiếp theo để dùng clip XV2DA hiện có.

Không tuyên bố thành công nếu chưa chạy test phù hợp. Nếu FFmpeg hoặc dependency không có trên máy, nói rõ phần nào đã được kiểm tra và phần nào chưa thể kiểm tra.

