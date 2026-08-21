"""ffprobe integration and JSON parsing."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from .exceptions import FFmpegMissingError, ProbeError


@dataclass(frozen=True)
class MediaInfo:
    duration: float
    has_video: bool
    has_audio: bool
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    video_codec: str | None = None
    pixel_format: str | None = None
    sample_rate: int | None = None
    channels: int | None = None


def require_tools() -> tuple[str, str]:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise FFmpegMissingError(
            "Khong tim thay ffmpeg/ffprobe trong PATH. Cai FFmpeg (vi du: winget install "
            "Gyan.FFmpeg), mo terminal moi va chay lai."
        )
    return ffmpeg, ffprobe


def parse_probe_json(data: dict[str, Any]) -> MediaInfo:
    streams = data.get("streams") or []
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    duration_value = (data.get("format") or {}).get("duration")
    if duration_value is None:
        durations = [float(s["duration"]) for s in streams if s.get("duration") is not None]
        duration_value = max(durations, default=0.0)
    fps: float | None = None
    if video:
        rate = video.get("avg_frame_rate") or video.get("r_frame_rate")
        if rate and rate != "0/0":
            fps = float(Fraction(rate))
    return MediaInfo(
        duration=float(duration_value or 0),
        has_video=video is not None,
        has_audio=audio is not None,
        width=video.get("width") if video else None,
        height=video.get("height") if video else None,
        fps=fps,
        video_codec=video.get("codec_name") if video else None,
        pixel_format=video.get("pix_fmt") if video else None,
        sample_rate=int(audio["sample_rate"]) if audio and audio.get("sample_rate") else None,
        channels=audio.get("channels") if audio else None,
    )


def probe_media(path: Path, timeout: int = 30) -> MediaInfo:
    _, ffprobe = require_tools()
    command = [
        ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ProbeError(f"Khong probe duoc {path}: {error}") from error
    if result.returncode:
        raise ProbeError(f"ffprobe that bai voi {path}: {result.stderr.strip()}")
    try:
        return parse_probe_json(json.loads(result.stdout))
    except (ValueError, TypeError, KeyError) as error:
        raise ProbeError(f"Du lieu ffprobe khong hop le cho {path}: {error}") from error
