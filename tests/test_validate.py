import pytest
import yaml

from video_factory.exceptions import ConfigurationError
from video_factory.paths import resolve_project_path
from video_factory.validate import validate_project


def test_safe_path(project_dir):
    assert resolve_project_path(project_dir, __import__("pathlib").Path("input/video/a.mp4")).parent.name == "video"
    with pytest.raises(ConfigurationError):
        resolve_project_path(project_dir, __import__("pathlib").Path("../secret.txt"))


def test_collects_all_missing_media(project_dir):
    result = validate_project(project_dir, check_tools=False)
    assert len(result.errors) == 2
    assert all("thieu file" in item for item in result.errors)


def test_caption_outside_timeline(project_dir, project_data):
    project_data["captions"] = [{"id": "late", "text": "Muộn", "start": 1, "end": 9}]
    (project_dir / "project.yaml").write_text(yaml.safe_dump(project_data), encoding="utf-8")
    result = validate_project(project_dir, check_tools=False)
    assert any("captions[0].end" in error for error in result.errors)


def test_scene_trim_exceeds_source(monkeypatch, project_dir):
    from video_factory.probe import MediaInfo
    for name in ("one.mp4", "two.mp4"):
        (project_dir / "input/video" / name).touch()
    monkeypatch.setattr("video_factory.validate.require_tools", lambda: ("ffmpeg", "ffprobe"))
    monkeypatch.setattr("video_factory.validate._check_filters", lambda *_: None)
    monkeypatch.setattr("video_factory.validate.probe_media", lambda _: MediaInfo(0.5, True, False, 320, 568, 24))
    result = validate_project(project_dir)
    assert sum("vuot duration" in error for error in result.errors) == 2

