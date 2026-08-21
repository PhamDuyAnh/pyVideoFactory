"""Build FFmpeg inputs and filters for project audio tracks."""

from pathlib import Path

from .models import AudioConfig, AudioTrack, Scene
from .paths import resolve_audio_file_path, resolve_project_path
from .timeline import build_timeline


def default_gain(track: AudioTrack, config: AudioConfig) -> float:
    if track.gain_db is not None:
        return track.gain_db
    return {
        "voice": config.default_voice_gain_db,
        "effect": config.default_effect_gain_db,
        "ambience": config.default_ambience_gain_db,
    }[track.role]


def audio_graph(
    tracks: list[AudioTrack],
    config: AudioConfig,
    project_dir: Path,
    total: float,
    scenes: list[Scene] | None = None,
) -> tuple[list[str], str]:
    """Return extra FFmpeg inputs and a filter_complex producing [mixed]."""
    inputs: list[str] = []
    chains: list[str] = []
    labels: list[str] = []
    input_index = 1  # input 0 is the composed silent video
    for scene, item in zip(scenes or [], build_timeline(scenes or []), strict=True):
        if not scene.source_audio:
            continue
        path = resolve_project_path(project_dir, scene.file, expected_root="input/video")
        inputs.extend(["-i", str(path)])
        delay = round(item.start * 1000)
        label = f"scene_a{input_index}"
        chains.append(
            f"[{input_index}:a]atrim=start={scene.start}:duration={scene.duration},"
            "asetpts=PTS-STARTPTS,"
            f"aformat=sample_fmts=fltp:sample_rates={config.sample_rate}:channel_layouts=stereo,"
            f"adelay={delay}|{delay}[{label}]"
        )
        labels.append(f"[{label}]")
        input_index += 1
    for index, track in enumerate(tracks):
        duration = track.duration
        if track.type == "file":
            path = resolve_audio_file_path(project_dir, track.file or Path(), track.role)
            inputs.extend(["-i", str(path)])
            source = f"[{input_index}:a]"
            input_index += 1
        elif track.type == "generated_tone":
            inputs.extend(["-f", "lavfi", "-t", str(duration), "-i", f"sine=frequency={track.frequency_hz}:sample_rate={config.sample_rate}"])
            source = f"[{input_index}:a]"
            input_index += 1
        elif track.type == "generated_noise":
            color = {"white": "white", "pink": "pink", "brown": "brown"}[track.noise]
            inputs.extend(["-f", "lavfi", "-t", str(duration), "-i", f"anoisesrc=color={color}:sample_rate={config.sample_rate}"])
            source = f"[{input_index}:a]"
            input_index += 1
        elif track.type == "generated_ticks":
            inputs.extend(["-f", "lavfi", "-t", str(duration), "-i", f"sine=frequency={track.frequency_hz}:sample_rate={config.sample_rate}:beep_factor=4"])
            source = f"[{input_index}:a]"
            input_index += 1
        else:
            inputs.extend(["-f", "lavfi", "-t", str(duration), "-i", f"anullsrc=r={config.sample_rate}:cl=stereo"])
            source = f"[{input_index}:a]"
            input_index += 1
        filters = [f"atrim=start={track.trim_start}" + (f":duration={duration}" if duration else ""), "asetpts=PTS-STARTPTS"]
        if track.type == "generated_ticks":
            filters.append("agate=threshold=0.2:ratio=10:attack=1:release=15")
            filters.append(f"tremolo=f={1 / track.interval}:d=1")
        if track.highpass_hz:
            filters.append(f"highpass=f={track.highpass_hz}")
        if track.lowpass_hz:
            filters.append(f"lowpass=f={track.lowpass_hz}")
        if track.radio_voice:
            filters.extend(["highpass=f=300", "lowpass=f=3200", "acompressor=threshold=-18dB:ratio=2:attack=10:release=100"])
        if track.fade_in:
            filters.append(f"afade=t=in:st=0:d={track.fade_in}")
        if track.fade_out and duration:
            filters.append(f"afade=t=out:st={max(0, duration - track.fade_out)}:d={track.fade_out}")
        filters.extend([
            f"volume={default_gain(track, config)}dB",
            f"aformat=sample_fmts=fltp:sample_rates={config.sample_rate}:channel_layouts=stereo",
            f"adelay={round(track.start * 1000)}|{round(track.start * 1000)}",
        ])
        label = f"a{index}"
        chains.append(f"{source}{','.join(filters)}[{label}]")
        labels.append(f"[{label}]")
    if not labels:
        chains.append(f"anullsrc=r={config.sample_rate}:cl=stereo,atrim=duration={total}[mixed]")
    else:
        chains.append(
            f"{''.join(labels)}amix=inputs={len(labels)}:duration=longest:normalize=0,"
            f"atrim=duration={total},apad=whole_dur={total}[mixed]"
        )
    return inputs, ";".join(chains)
