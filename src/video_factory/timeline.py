"""Pure timeline calculation."""

from dataclasses import asdict, dataclass

from .models import Scene


@dataclass(frozen=True)
class TimelineScene:
    id: str
    start: float
    end: float
    duration: float
    transition_after: str
    transition_duration: float


def build_timeline(scenes: list[Scene]) -> list[TimelineScene]:
    """Place scenes, subtracting crossfade overlaps from the final duration."""
    result: list[TimelineScene] = []
    cursor = 0.0
    for index, scene in enumerate(scenes):
        end = cursor + scene.duration
        transition = scene.transition_after
        if transition.duration >= scene.duration:
            raise ValueError(f"scenes[{index}].transition_after.duration must be shorter than scene")
        result.append(
            TimelineScene(
                id=scene.id,
                start=cursor,
                end=end,
                duration=scene.duration,
                transition_after=transition.type,
                transition_duration=transition.duration,
            )
        )
        cursor = end - (transition.duration if transition.type == "crossfade" else 0.0)
    return result


def timeline_duration(scenes: list[Scene]) -> float:
    timeline = build_timeline(scenes)
    return timeline[-1].end if timeline else 0.0


def timeline_as_dicts(scenes: list[Scene]) -> list[dict[str, object]]:
    return [asdict(item) for item in build_timeline(scenes)]

