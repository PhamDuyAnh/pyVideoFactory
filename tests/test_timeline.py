from video_factory.models import Scene, Transition
from video_factory.timeline import build_timeline, timeline_duration


def test_cut_duration():
    scenes = [Scene(id="a", file="a.mp4", duration=2), Scene(id="b", file="b.mp4", duration=3)]
    assert timeline_duration(scenes) == 5


def test_crossfade_offsets():
    scenes = [
        Scene(id="a", file="a.mp4", duration=2, transition_after=Transition(type="crossfade", duration=0.25)),
        Scene(id="b", file="b.mp4", duration=3),
    ]
    timeline = build_timeline(scenes)
    assert timeline[1].start == 1.75
    assert timeline_duration(scenes) == 4.75

