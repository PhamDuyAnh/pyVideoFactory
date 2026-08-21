"""Safe project-relative path handling."""

from pathlib import Path

from .exceptions import ConfigurationError


def resolve_project_path(project_dir: Path, value: Path, *, expected_root: str | None = None) -> Path:
    """Resolve a relative YAML path and prevent escape from the project directory."""
    if value.is_absolute():
        raise ConfigurationError(f"Duong dan phai tuong doi voi project: {value}")
    root = project_dir.resolve()
    result = (root / value).resolve()
    try:
        result.relative_to(root)
    except ValueError as error:
        raise ConfigurationError(f"Duong dan vuot ra ngoai project: {value}") from error
    if expected_root:
        allowed = (root / expected_root).resolve()
        try:
            result.relative_to(allowed)
        except ValueError as error:
            raise ConfigurationError(f"Duong dan phai nam trong {expected_root}/: {value}") from error
    return result


def ensure_project_layout(project_dir: Path) -> None:
    """Create only generated/output directories, never touching input files."""
    for relative in ("input/video", "input/audio", "work", "output"):
        (project_dir / relative).mkdir(parents=True, exist_ok=True)

