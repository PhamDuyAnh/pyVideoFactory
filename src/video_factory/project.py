"""Project creation and safe cleanup."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from .exceptions import ConfigurationError


def repository_root() -> Path:
    return Path(__file__).resolve().parents[2]


def create_project(name: str, root: Path | None = None) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]*", name):
        raise ConfigurationError("Ten project chi dung chu thuong ASCII, so, '_' hoac '-'")
    root = (root or repository_root()).resolve()
    destination = root / "projects" / name
    if destination.exists():
        raise ConfigurationError(f"Project da ton tai: {destination}")
    destination.mkdir(parents=True)
    for relative in ("input/video", "input/audio", "work", "output"):
        (destination / relative).mkdir(parents=True)
    template = root / "assets" / "templates" / "project.yaml"
    content = template.read_text(encoding="utf-8").replace("PROJECT_ID", name).replace("PROJECT_TITLE", name.replace("_", " ").title())
    (destination / "project.yaml").write_text(content, encoding="utf-8")
    (destination / "README.md").write_text(f"# {name}\n\nDat clip vao `input/video/`, audio vao `input/audio/`, sau do sua `project.yaml`.\n", encoding="utf-8")
    for folder, label in (("input/video", "clip video"), ("input/audio", "audio")):
        (destination / folder / "README.md").write_text(f"Dat {label} cua project tai day.\n", encoding="utf-8")
    (destination / "work" / ".gitkeep").touch()
    (destination / "output" / ".gitkeep").touch()
    return destination


def clean_project(project: Path, *, include_output: bool = False) -> None:
    project = project.resolve()
    for folder_name in (["work", "output"] if include_output else ["work"]):
        folder = (project / folder_name).resolve()
        if folder.parent != project or folder.name not in {"work", "output"}:
            raise ConfigurationError(f"Tu choi xoa duong dan khong an toan: {folder}")
        if folder.exists():
            for child in folder.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                elif child.name != ".gitkeep":
                    child.unlink()
        folder.mkdir(exist_ok=True)
        (folder / ".gitkeep").touch(exist_ok=True)

