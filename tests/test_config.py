import pytest
import yaml

from video_factory.config import load_config
from video_factory.exceptions import ConfigurationError


def test_load_valid_yaml(project_dir):
    assert load_config(project_dir).project.id == "test_video"


def test_unknown_field_is_reported(project_dir, project_data):
    project_data["video"]["typo_fps"] = 24
    (project_dir / "project.yaml").write_text(yaml.safe_dump(project_data), encoding="utf-8")
    with pytest.raises(ConfigurationError, match=r"video.typo_fps"):
        load_config(project_dir)


def test_missing_field_path(project_dir, project_data):
    del project_data["project"]["title"]
    (project_dir / "project.yaml").write_text(yaml.safe_dump(project_data), encoding="utf-8")
    with pytest.raises(ConfigurationError, match=r"project.title"):
        load_config(project_dir)

