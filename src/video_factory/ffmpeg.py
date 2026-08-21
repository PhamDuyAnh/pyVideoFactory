"""Safe FFmpeg command execution and filter escaping."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import TextIO

from .exceptions import RenderError


def quote_command(command: list[str]) -> str:
    return subprocess.list2cmdline(command)


def filter_path(path: Path) -> str:
    """Escape a Windows/POSIX path for an FFmpeg filter argument."""
    return str(path.resolve()).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")


def run_ffmpeg(command: list[str], log: TextIO, stage: str) -> None:
    log.write(f"\n[{stage}]\n$ {quote_command(command)}\n")
    log.flush()
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=False)
    if result.returncode:
        raise RenderError(f"Stage '{stage}' that bai (exit {result.returncode})")

