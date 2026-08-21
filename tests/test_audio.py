from pathlib import Path

from video_factory.audio import audio_graph
from video_factory.models import AudioConfig, Scene, Transition


def test_source_audio_is_trimmed_and_delayed_on_timeline(tmp_path: Path):
    video = tmp_path / "input" / "video" / "source.mp4"
    video.parent.mkdir(parents=True)
    video.touch()
    scenes = [
        Scene(id="silent", file=Path("input/video/source.mp4"), duration=2),
        Scene(
            id="voiced",
            file=Path("input/video/source.mp4"),
            start=0.4,
            duration=3,
            source_audio=True,
        ),
    ]

    inputs, graph = audio_graph([], AudioConfig(), tmp_path, 5, scenes)

    assert inputs == ["-i", str(video)]
    assert "atrim=start=0.4:duration=3.0" in graph
    assert "adelay=2000|2000" in graph
    assert "apad=whole_dur=5" in graph


def test_source_audio_uses_crossfade_adjusted_scene_start(tmp_path: Path):
    video = tmp_path / "input" / "video" / "source.mp4"
    video.parent.mkdir(parents=True)
    video.touch()
    scenes = [
        Scene(
            id="first",
            file=Path("input/video/source.mp4"),
            duration=2,
            transition_after=Transition(type="crossfade", duration=0.25),
        ),
        Scene(
            id="second",
            file=Path("input/video/source.mp4"),
            duration=3,
            source_audio=True,
        ),
    ]

    _, graph = audio_graph([], AudioConfig(), tmp_path, 4.75, scenes)

    assert "adelay=1750|1750" in graph
