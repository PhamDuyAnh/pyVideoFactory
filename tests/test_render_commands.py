from pathlib import Path

from video_factory.models import ProjectConfig
from video_factory.render import _compose_command


def test_mixed_cut_and_crossfade_use_matching_filters():
    config = ProjectConfig.model_validate(
        {
            "project": {"id": "test", "title": "Test"},
            "scenes": [
                {
                    "id": "a",
                    "file": "input/video/a.mp4",
                    "duration": 2,
                    "transition_after": {"type": "cut", "duration": 0},
                },
                {
                    "id": "b",
                    "file": "input/video/b.mp4",
                    "duration": 3,
                    "transition_after": {"type": "crossfade", "duration": 0.25},
                },
                {"id": "c", "file": "input/video/c.mp4", "duration": 4},
            ],
        }
    )

    command = _compose_command(
        "ffmpeg",
        config,
        [Path("a.mp4"), Path("b.mp4"), Path("c.mp4")],
        Path("output.mp4"),
    )
    graph = command[command.index("-filter_complex") + 1]

    assert "settb=AVTB,setpts=PTS-STARTPTS" in graph
    assert "[s0][s1]concat=n=2:v=1:a=0[x1]" in graph
    assert "[x1][s2]xfade=transition=fade:duration=0.25:offset=4.75[v]" in graph
