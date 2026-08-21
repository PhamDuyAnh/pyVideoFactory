import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from video_factory.render import render_project
from video_factory.validate import validate_project


@pytest.mark.skipif(not shutil.which("ffmpeg") or not shutil.which("ffprobe"), reason="FFmpeg/ffprobe khong co trong PATH")
def test_smoke_render(tmp_path: Path):
    ffmpeg = shutil.which("ffmpeg")
    for folder in ("input/video", "input/audio", "work", "output"):
        (tmp_path / folder).mkdir(parents=True)
    for index, color in enumerate(("red", "blue"), 1):
        subprocess.run([ffmpeg, "-y", "-f", "lavfi", "-i", f"color=c={color}:s=160x284:r=24:d=1", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(tmp_path / "input/video" / f"s{index}.mp4")], check=True, capture_output=True)
    data = {"schema_version": 1, "project": {"id": "smoke", "title": "Smoke"}, "video": {"width": 160, "height": 284, "fps": 24, "preset": "ultrafast"}, "style": {"font_name": "Arial", "font_size": 20, "margin_bottom": 30}, "scenes": [{"id": "a", "file": "input/video/s1.mp4", "duration": 1, "transition_after": {"type": "crossfade", "duration": 0.1}}, {"id": "b", "file": "input/video/s2.mp4", "duration": 1}], "captions": [{"id": "c", "text": "Tiếng Việt rõ", "start": 0.2, "end": 1.5}], "audio_tracks": [{"id": "tone", "type": "generated_tone", "duration": 1.8, "start": 0, "gain_db": -20}], "outputs": {"master": {"file": "output/master.mp4", "width": 160, "height": 284}, "preview": {"enabled": True, "file": "output/preview.mp4", "width": 81, "height": 144, "crf": 30}, "report": {"file": "output/report.json"}}}
    (tmp_path / "project.yaml").write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    validation = validate_project(tmp_path)
    assert validation.ok, validation.errors
    render_project(tmp_path, validation)
    from video_factory.probe import probe_media
    info = probe_media(tmp_path / "output/master.mp4")
    assert info.has_video and info.has_audio
    assert (info.width, info.height) == (160, 284)
    assert info.pixel_format == "yuv420p"
    assert abs(info.duration - 1.9) < 0.15
