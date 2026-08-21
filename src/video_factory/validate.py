"""Aggregate project validation without fail-fast behavior."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from .config import load_config
from .exceptions import ConfigurationError, FFmpegMissingError, ProbeError
from .models import ProjectConfig
from .paths import resolve_project_path
from .probe import MediaInfo, probe_media, require_tools
from .timeline import build_timeline, timeline_duration


@dataclass
class ValidationResult:
    config: ProjectConfig | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    media: dict[str, MediaInfo] = field(default_factory=dict)
    duration: float = 0.0

    @property
    def ok(self) -> bool:
        return not self.errors


def _check_filters(ffmpeg: str, result: ValidationResult) -> None:
    completed = subprocess.run(
        [ffmpeg, "-hide_banner", "-filters"], capture_output=True, text=True, check=False
    )
    listing = completed.stdout + completed.stderr
    for name in ("scale", "fps", "amix", "loudnorm"):
        if name not in listing:
            result.errors.append(f"FFmpeg thieu filter bat buoc: {name}")
    if " subtitles " not in listing and " ass " not in listing:
        result.errors.append("FFmpeg thieu filter subtitles/ass (libass)")


def validate_project(project_dir: Path, *, check_tools: bool = True) -> ValidationResult:
    project_dir = project_dir.resolve()
    result = ValidationResult()
    try:
        config = load_config(project_dir)
    except ConfigurationError as error:
        result.errors.extend(str(error).splitlines())
        return result
    result.config = config
    try:
        timeline = build_timeline(config.scenes)
        result.duration = timeline_duration(config.scenes)
    except ValueError as error:
        result.errors.append(str(error))
        timeline = []

    if check_tools:
        try:
            ffmpeg, _ = require_tools()
            _check_filters(ffmpeg, result)
        except FFmpegMissingError as error:
            result.errors.append(str(error))

    for index, scene in enumerate(config.scenes):
        try:
            path = resolve_project_path(project_dir, scene.file, expected_root="input/video")
        except ConfigurationError as error:
            result.errors.append(f"scenes[{index}].file: {error}")
            continue
        if not path.is_file():
            result.errors.append(f"scenes[{index}].file: thieu file {path}")
            continue
        if not check_tools:
            continue
        try:
            info = probe_media(path)
            result.media[str(scene.file)] = info
            if not info.has_video:
                result.errors.append(f"scenes[{index}].file: file khong co video stream")
            tolerance = max(0.05, 1 / config.video.fps)
            if scene.start + scene.duration > info.duration + tolerance:
                result.errors.append(
                    f"scenes[{index}].duration: trim ket thuc {scene.start + scene.duration:.3f}s "
                    f"vuot duration nguon {info.duration:.3f}s"
                )
            if (info.width, info.height) != (config.video.width, config.video.height):
                result.warnings.append(
                    f"Scene {scene.id}: {info.width}x{info.height} se duoc scale/crop"
                )
            if info.fps and abs(info.fps - config.video.fps) > 0.01:
                result.warnings.append(f"Scene {scene.id}: {info.fps:.3f} fps se doi thanh {config.video.fps:g}")
        except ProbeError as error:
            result.errors.append(f"scenes[{index}].file: {error}")

    for index, track in enumerate(config.audio_tracks):
        if track.type != "file" or track.file is None:
            continue
        try:
            path = resolve_project_path(project_dir, track.file, expected_root="input/audio")
        except ConfigurationError as error:
            result.errors.append(f"audio_tracks[{index}].file: {error}")
            continue
        if not path.is_file():
            result.errors.append(f"audio_tracks[{index}].file: thieu file {path}")
        elif check_tools:
            try:
                info = probe_media(path)
                result.media[str(track.file)] = info
                if not info.has_audio:
                    result.errors.append(f"audio_tracks[{index}].file: file khong co audio stream")
                available = max(0, info.duration - track.trim_start)
                if track.duration and track.duration > available + 0.05:
                    result.errors.append(f"audio_tracks[{index}].duration: vuot audio nguon")
            except ProbeError as error:
                result.errors.append(f"audio_tracks[{index}].file: {error}")

    for index, caption in enumerate(config.captions):
        if caption.end > result.duration + 1 / config.video.fps:
            result.errors.append(
                f"captions[{index}].end: {caption.end:.3f}s vuot timeline {result.duration:.3f}s"
            )
        if len(caption.text) > 90 or caption.text.count("\n") > 1:
            result.warnings.append(f"Caption {caption.id} co the qua dai cho man hinh dien thoai")

    for index, scene in enumerate(timeline):
        if scene.transition_after == "crossfade" and index == len(timeline) - 1:
            result.warnings.append("Transition sau scene cuoi khong co tac dung")

    if config.style.font_file:
        try:
            font = resolve_project_path(project_dir, config.style.font_file)
            if not font.is_file():
                result.warnings.append(
                    f"Khong tim thay font {font}; libass se dung fallback '{config.style.font_name}'"
                )
        except ConfigurationError as error:
            result.errors.append(f"style.font_file: {error}")
    return result

