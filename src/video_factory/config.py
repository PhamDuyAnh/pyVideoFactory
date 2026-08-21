"""Load and validate project configuration."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .exceptions import ConfigurationError
from .models import ProjectConfig


def format_validation_error(error: ValidationError) -> str:
    """Return Pydantic errors with YAML-friendly field paths."""
    lines: list[str] = []
    for item in error.errors(include_url=False):
        path = ""
        for part in item["loc"]:
            path += f"[{part}]" if isinstance(part, int) else ("." if path else "") + str(part)
        lines.append(f"{path}: {item['msg']}")
    return "\n".join(lines)


def load_config(project_dir: Path) -> ProjectConfig:
    """Load project.yaml in *project_dir* using the strict schema."""
    config_path = project_dir.resolve() / "project.yaml"
    if not config_path.is_file():
        raise ConfigurationError(f"Khong tim thay file cau hinh: {config_path}")
    try:
        raw: Any = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ConfigurationError(f"Khong doc duoc YAML {config_path}: {error}") from error
    if not isinstance(raw, dict):
        raise ConfigurationError("project.yaml phai chua mot YAML mapping o cap cao nhat")
    try:
        return ProjectConfig.model_validate(raw)
    except ValidationError as error:
        raise ConfigurationError("Cau hinh khong hop le:\n" + format_validation_error(error)) from error

