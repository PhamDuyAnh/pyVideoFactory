"""Multi-stage, debuggable FFmpeg rendering pipeline."""

from __future__ import annotations

import hashlib
import json
import platform
import re
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import __version__
from .audio import audio_graph
from .exceptions import RenderError
from .ffmpeg import filter_path, quote_command, run_ffmpeg
from .logging_utils import stage
from .models import ProjectConfig, Scene
from .paths import ensure_project_layout, resolve_project_path
from .probe import probe_media, require_tools
from .subtitles import write_ass
from .timeline import timeline_as_dicts, timeline_duration
from .validate import ValidationResult


def _scale_filter(config: ProjectConfig, scene: Scene) -> str:
    width, height = config.video.width, config.video.height
    mode = scene.scale_mode or config.video.scale_mode
    if mode == "cover":
        return f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color={config.video.background_color}"
    )


def _normalize_command(ffmpeg: str, config: ProjectConfig, project: Path, scene: Scene, output: Path) -> list[str]:
    source = resolve_project_path(project, scene.file, expected_root="input/video")
    video_filter = f"{_scale_filter(config, scene)},fps={config.video.fps},setsar=1,format={config.video.pixel_format}"
    command = [ffmpeg, "-hide_banner", "-y", "-ss", str(scene.start), "-t", str(scene.duration), "-i", str(source)]
    if scene.source_audio:
        audio_map = ["-map", "0:a:0?", "-c:a", "aac", "-ar", str(config.audio.sample_rate), "-ac", "2"]
    else:
        audio_map = ["-an"]
    return command + ["-map", "0:v:0", "-vf", video_filter, "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", *audio_map, str(output)]


def _compose_command(ffmpeg: str, config: ProjectConfig, scene_files: list[Path], output: Path) -> list[str]:
    command = [ffmpeg, "-hide_banner", "-y"]
    for path in scene_files:
        command.extend(["-i", str(path)])
    has_crossfade = any(s.transition_after.type == "crossfade" for s in config.scenes[:-1])
    if not has_crossfade:
        graph = "".join(f"[{i}:v]" for i in range(len(scene_files))) + f"concat=n={len(scene_files)}:v=1:a=0[v]"
    else:
        chains: list[str] = []
        current = "[0:v]"
        elapsed = config.scenes[0].duration
        for index, previous in enumerate(config.scenes[:-1], start=1):
            label = "v" if index == len(scene_files) - 1 else f"x{index}"
            overlap = previous.transition_after.duration if previous.transition_after.type == "crossfade" else 0.001
            offset = max(0, elapsed - overlap)
            chains.append(f"{current}[{index}:v]xfade=transition=fade:duration={overlap}:offset={offset}[{label}]")
            current = f"[{label}]"
            elapsed += config.scenes[index].duration - overlap
        graph = ";".join(chains)
    return command + ["-filter_complex", graph, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "17", "-preset", "veryfast", str(output)]


def _parse_loudnorm(stderr: str) -> dict[str, str]:
    matches = re.findall(r"\{\s*\"input_i\".*?\}", stderr, re.DOTALL)
    if not matches:
        raise RenderError("FFmpeg khong tra ve thong ke loudnorm luot 1")
    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError as error:
        raise RenderError(f"Khong doc duoc thong ke loudnorm: {error}") from error


def _loudnorm_filter(config: ProjectConfig, measured: dict[str, str] | None = None) -> str:
    base = f"loudnorm=I={config.audio.target_lufs}:TP={config.audio.true_peak_db}:LRA=11"
    if measured is None:
        return base + ":print_format=json"
    return (
        base
        + f":measured_I={measured['input_i']}:measured_TP={measured['input_tp']}"
        + f":measured_LRA={measured['input_lra']}:measured_thresh={measured['input_thresh']}"
        + f":offset={measured['target_offset']}:linear=true:print_format=summary"
    )


def _file_fingerprint(path: Path) -> dict[str, Any]:
    stat = path.stat()
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        digest.update(stream.read(1024 * 1024))
    return {"path": str(path), "size": stat.st_size, "mtime": stat.st_mtime, "sha256_first_1m": digest.hexdigest()}


def planned_commands(config: ProjectConfig, project: Path) -> list[list[str]]:
    ffmpeg, _ = require_tools()
    work = project / "work"
    scene_files = [work / "scenes" / f"{index:03d}_{scene.id}.mp4" for index, scene in enumerate(config.scenes, 1)]
    commands = [_normalize_command(ffmpeg, config, project, scene, output) for scene, output in zip(config.scenes, scene_files, strict=True)]
    commands.append(_compose_command(ffmpeg, config, scene_files, work / "timeline.mp4"))
    return commands


def render_project(project: Path, validation: ValidationResult, *, overwrite: bool = False, dry_run: bool = False) -> dict[str, Any]:
    if not validation.config:
        raise RenderError("Khong co cau hinh hop le")
    config = validation.config
    ffmpeg, _ = require_tools()
    project = project.resolve()
    ensure_project_layout(project)
    master = resolve_project_path(project, config.outputs.master.file, expected_root="output")
    preview = resolve_project_path(project, config.outputs.preview.file, expected_root="output")
    report_path = resolve_project_path(project, config.outputs.report.file, expected_root="output")
    existing = [path for path in (master, preview if config.outputs.preview.enabled else None) if path and path.exists()]
    if existing and not overwrite and not dry_run:
        raise RenderError("Output da ton tai; dung --overwrite de ghi de: " + ", ".join(map(str, existing)))
    commands = planned_commands(config, project)
    if dry_run:
        return {"duration": validation.duration, "timeline": timeline_as_dicts(config.scenes), "commands": [quote_command(c) for c in commands]}

    started = time.perf_counter()
    timings: dict[str, float] = {}
    work = project / "work"
    scenes_dir = work / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    log_path = project / "output" / "render.log"
    timeline_path = work / "timeline.json"
    timeline_path.write_text(json.dumps(timeline_as_dicts(config.scenes), ensure_ascii=False, indent=2), encoding="utf-8")
    scene_files = [scenes_dir / f"{index:03d}_{scene.id}.mp4" for index, scene in enumerate(config.scenes, 1)]
    with log_path.open("w", encoding="utf-8") as log:
        try:
            point = time.perf_counter()
            for index, (scene, output) in enumerate(zip(config.scenes, scene_files, strict=True), 1):
                stage(f"1/6 Chuan hoa scene {index}/{len(scene_files)}: {scene.id}")
                run_ffmpeg(_normalize_command(ffmpeg, config, project, scene, output), log, f"normalize:{scene.id}")
            timings["normalize_scenes"] = time.perf_counter() - point

            point = time.perf_counter()
            stage("2/6 Ghep timeline")
            timeline_video = work / "timeline.mp4"
            run_ffmpeg(_compose_command(ffmpeg, config, scene_files, timeline_video), log, "compose_timeline")
            timings["compose_timeline"] = time.perf_counter() - point

            point = time.perf_counter()
            stage("3/6 Burn caption")
            ass_path = work / "subtitles.ass"
            write_ass(ass_path, config.captions, config.style, config.video.width, config.video.height)
            captioned = work / "captioned.mp4"
            subtitle_filter = f"subtitles='{filter_path(ass_path)}'"
            if config.style.font_file:
                font = resolve_project_path(project, config.style.font_file)
                if font.exists():
                    subtitle_filter += f":fontsdir='{filter_path(font.parent)}'"
            run_ffmpeg([ffmpeg, "-hide_banner", "-y", "-i", str(timeline_video), "-vf", subtitle_filter, "-an", "-c:v", "libx264", "-crf", "18", "-preset", config.video.preset, str(captioned)], log, "burn_subtitles")
            timings["subtitles"] = time.perf_counter() - point

            point = time.perf_counter()
            stage("4/6 Tron audio va loudnorm luot 1")
            extra_inputs, graph = audio_graph(config.audio_tracks, config.audio, project, validation.duration)
            pass1 = [ffmpeg, "-hide_banner", "-i", str(captioned), *extra_inputs, "-filter_complex", graph + f";[mixed]{_loudnorm_filter(config)}[norm]", "-map", "[norm]", "-f", "null", "-"]
            log.write("\n[loudnorm_pass1]\n$ " + quote_command(pass1) + "\n")
            result = subprocess.run(pass1, capture_output=True, text=True, check=False)
            log.write(result.stdout + result.stderr)
            if result.returncode:
                raise RenderError("Loudnorm luot 1 that bai")
            measured = _parse_loudnorm(result.stderr)

            stage("5/6 Tao master")
            master_command = [ffmpeg, "-hide_banner", "-y", "-i", str(captioned), *extra_inputs, "-filter_complex", graph + f";[mixed]{_loudnorm_filter(config, measured)}[norm]", "-map", "0:v:0", "-map", "[norm]", "-c:v", config.video.video_codec, "-crf", str(config.video.crf), "-preset", config.video.preset, "-pix_fmt", config.video.pixel_format, "-c:a", "aac", "-b:a", "192k", "-ar", str(config.audio.sample_rate), "-ac", "2", "-movflags", "+faststart", "-metadata", f"title={config.project.title}", "-metadata", f"comment={config.project.description}", "-shortest", str(master)]
            run_ffmpeg(master_command, log, "master")
            timings["audio_and_master"] = time.perf_counter() - point

            point = time.perf_counter()
            if config.outputs.preview.enabled:
                stage("6/6 Tao preview")
                run_ffmpeg([ffmpeg, "-hide_banner", "-y", "-i", str(master), "-vf", f"scale={config.outputs.preview.width}:{config.outputs.preview.height}", "-c:v", "libx264", "-crf", str(config.outputs.preview.crf), "-preset", "veryfast", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(preview)], log, "preview")
            timings["preview"] = time.perf_counter() - point
        except RenderError as error:
            log.write(f"\nFAILED: {error}\n")
            raise RenderError(f"{error}. Xem log: {log_path}") from error

    actual = probe_media(master).duration
    inputs = [resolve_project_path(project, scene.file) for scene in config.scenes]
    inputs.extend(resolve_project_path(project, track.file) for track in config.audio_tracks if track.file)
    report = {
        "application_version": __version__, "rendered_at": datetime.now(UTC).isoformat(),
        "python_version": platform.python_version(), "ffmpeg_version": subprocess.run([ffmpeg, "-version"], capture_output=True, text=True, check=False).stdout.splitlines()[0],
        "inputs": [_file_fingerprint(path) for path in inputs], "timeline": timeline_as_dicts(config.scenes),
        "expected_duration": timeline_duration(config.scenes), "actual_duration": actual,
        "master": {"file": str(master), "width": config.outputs.master.width, "height": config.outputs.master.height},
        "preview": {"enabled": config.outputs.preview.enabled, "file": str(preview) if config.outputs.preview.enabled else None},
        "warnings": validation.warnings, "stage_seconds": timings, "total_seconds": time.perf_counter() - started, "success": True,
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report
