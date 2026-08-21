from pathlib import Path

from video_factory.ffmpeg import filter_path, quote_command


def test_windows_argument_quoting():
    command = quote_command(["ffmpeg", "-i", r"C:\My Clips\a.mp4"])
    assert '"C:\\My Clips\\a.mp4"' in command


def test_filter_path_escapes_drive(monkeypatch):
    monkeypatch.setattr(Path, "resolve", lambda self: Path(r"C:\Video Work\sub.ass"))
    assert r"C\:/Video Work/sub.ass" in filter_path(Path("ignored"))

