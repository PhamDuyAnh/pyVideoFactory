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


def find_repository_root(project_dir: Path) -> Path:
    """Find the repository owning a project without trusting its YAML paths."""
    for candidate in (project_dir.resolve(), *project_dir.resolve().parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "assets").is_dir():
            return candidate
    raise ConfigurationError(f"Khong xac dinh duoc repository cho project: {project_dir}")


def resolve_shared_asset_path(project_dir: Path, value: Path, asset_root: str) -> Path:
    """Resolve a project-relative path strictly inside repository/assets/<asset_root>."""
    if value.is_absolute():
        raise ConfigurationError(f"Duong dan asset phai la duong dan tuong doi: {value}")
    repository = find_repository_root(project_dir)
    assets = (repository / "assets" / asset_root).resolve()
    result = (project_dir.resolve() / value).resolve()
    try:
        result.relative_to(repository)
    except ValueError as error:
        raise ConfigurationError(f"Duong dan asset thoat khoi repository: {value}") from error
    try:
        result.relative_to(assets)
    except ValueError as error:
        raise ConfigurationError(f"Duong dan asset phai nam trong assets/{asset_root}/: {value}") from error
    return result


def resolve_audio_file_path(project_dir: Path, value: Path, role: str) -> Path:
    """Allow project audio, plus repository shared audio for effect/ambience roles."""
    try:
        return resolve_project_path(project_dir, value, expected_root="input/audio")
    except ConfigurationError as project_error:
        if role not in {"effect", "ambience"}:
            raise project_error
        return resolve_shared_asset_path(project_dir, value, "audio")


def ensure_project_layout(project_dir: Path) -> None:
    """Create only generated/output directories, never touching input files."""
    for relative in ("input/video", "input/audio", "work", "output"):
        (project_dir / relative).mkdir(parents=True, exist_ok=True)
