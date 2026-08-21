from pathlib import Path

import pytest
import yaml


@pytest.fixture
def project_data() -> dict:
    return {
        "schema_version": 1,
        "project": {"id": "test_video", "title": "Test"},
        "video": {"width": 320, "height": 568, "fps": 24},
        "scenes": [
            {"id": "one", "file": "input/video/one.mp4", "start": 0, "duration": 1},
            {"id": "two", "file": "input/video/two.mp4", "start": 0, "duration": 1},
        ],
    }


@pytest.fixture
def project_dir(tmp_path: Path, project_data: dict) -> Path:
    for folder in ("input/video", "input/audio", "work", "output"):
        (tmp_path / folder).mkdir(parents=True)
    (tmp_path / "project.yaml").write_text(yaml.safe_dump(project_data), encoding="utf-8")
    return tmp_path

