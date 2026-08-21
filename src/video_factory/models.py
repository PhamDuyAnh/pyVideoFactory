"""Strict Pydantic models for project.yaml."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Alignment(StrEnum):
    bottom_center = "bottom_center"
    center = "center"
    top_center = "top_center"


class ProjectInfo(StrictModel):
    id: str = Field(min_length=1, pattern=r"^[A-Za-z0-9_-]+$")
    title: str = Field(min_length=1)
    description: str = ""


class VideoConfig(StrictModel):
    width: int = Field(default=1080, gt=0)
    height: int = Field(default=1920, gt=0)
    fps: float = Field(default=24, gt=0, le=120)
    background_color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    video_codec: str = "libx264"
    pixel_format: str = "yuv420p"
    crf: int = Field(default=19, ge=0, le=51)
    preset: str = "medium"
    scale_mode: str = Field(default="cover", pattern=r"^(cover|contain)$")


class AudioConfig(StrictModel):
    sample_rate: int = Field(default=48000, gt=0)
    channels: int = Field(default=2, ge=1, le=2)
    target_lufs: float = Field(default=-14.0, ge=-70, le=-5)
    true_peak_db: float = Field(default=-1.5, ge=-9, le=0)
    default_voice_gain_db: float = 0.0
    default_effect_gain_db: float = -12.0
    default_ambience_gain_db: float = -24.0


class StyleConfig(StrictModel):
    font_file: Path | None = None
    font_name: str = "Arial"
    font_size: int = Field(default=66, gt=0)
    primary_color: str = Field(default="#FFFFFF", pattern=r"^#[0-9A-Fa-f]{6}$")
    outline_color: str = Field(default="#000000", pattern=r"^#[0-9A-Fa-f]{6}$")
    outline_width: int = Field(default=4, ge=0)
    shadow: int = Field(default=1, ge=0)
    alignment: Alignment = Alignment.bottom_center
    margin_left: int = Field(default=80, ge=0)
    margin_right: int = Field(default=80, ge=0)
    margin_bottom: int = Field(default=250, ge=0)


class Transition(StrictModel):
    type: str = Field(default="cut", pattern=r"^(cut|crossfade)$")
    duration: float = Field(default=0.0, ge=0)

    @model_validator(mode="after")
    def check_duration(self) -> Transition:
        if self.type == "cut" and self.duration != 0:
            raise ValueError("cut transition must have duration 0")
        if self.type == "crossfade" and self.duration <= 0:
            raise ValueError("crossfade transition must have duration > 0")
        return self


class Scene(StrictModel):
    id: str = Field(min_length=1)
    file: Path
    start: float = Field(default=0.0, ge=0)
    duration: float = Field(gt=0)
    source_audio: bool = False
    scale_mode: str | None = Field(default=None, pattern=r"^(cover|contain)$")
    transition_after: Transition = Field(default_factory=Transition)


class Caption(StrictModel):
    id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    start: float = Field(ge=0)
    end: float = Field(gt=0)
    position: Alignment = Alignment.bottom_center

    @model_validator(mode="after")
    def check_times(self) -> Caption:
        if self.end <= self.start:
            raise ValueError("end must be greater than start")
        return self


class AudioTrack(StrictModel):
    id: str = Field(min_length=1)
    type: str = Field(pattern=r"^(file|generated_tone|generated_noise|generated_ticks|silence)$")
    role: str = Field(default="effect", pattern=r"^(voice|effect|ambience)$")
    file: Path | None = None
    start: float = Field(default=0.0, ge=0)
    duration: float | None = Field(default=None, gt=0)
    trim_start: float = Field(default=0.0, ge=0)
    gain_db: float | None = None
    fade_in: float = Field(default=0.0, ge=0)
    fade_out: float = Field(default=0.0, ge=0)
    frequency_hz: float = Field(default=1000, gt=0)
    noise: str = Field(default="pink", pattern=r"^(white|pink|brown)$")
    highpass_hz: float | None = Field(default=None, gt=0)
    lowpass_hz: float | None = Field(default=None, gt=0)
    interval: float = Field(default=0.2, gt=0)
    radio_voice: bool = False

    @model_validator(mode="after")
    def check_type_fields(self) -> AudioTrack:
        if self.type == "file" and self.file is None:
            raise ValueError("file is required when type=file")
        if self.type != "file" and self.duration is None:
            raise ValueError("duration is required for generated/silence tracks")
        if self.fade_in + self.fade_out > (self.duration or float("inf")):
            raise ValueError("fade_in + fade_out exceeds duration")
        return self


class MasterOutput(StrictModel):
    file: Path = Path("output/final_short_1080p.mp4")
    width: int = Field(default=1080, gt=0)
    height: int = Field(default=1920, gt=0)


class PreviewOutput(StrictModel):
    enabled: bool = True
    file: Path = Path("output/preview_720p.mp4")
    width: int = Field(default=405, gt=0)
    height: int = Field(default=720, gt=0)
    crf: int = Field(default=25, ge=0, le=51)


class ReportOutput(StrictModel):
    file: Path = Path("output/render_report.json")


class Outputs(StrictModel):
    master: MasterOutput = Field(default_factory=MasterOutput)
    preview: PreviewOutput = Field(default_factory=PreviewOutput)
    report: ReportOutput = Field(default_factory=ReportOutput)


class ProjectConfig(StrictModel):
    schema_version: int = Field(default=1, ge=1, le=1)
    project: ProjectInfo
    video: VideoConfig = Field(default_factory=VideoConfig)
    audio: AudioConfig = Field(default_factory=AudioConfig)
    style: StyleConfig = Field(default_factory=StyleConfig)
    scenes: list[Scene] = Field(min_length=1)
    captions: list[Caption] = Field(default_factory=list)
    audio_tracks: list[AudioTrack] = Field(default_factory=list)
    outputs: Outputs = Field(default_factory=Outputs)

    @field_validator("scenes")
    @classmethod
    def unique_scene_ids(cls, value: list[Scene]) -> list[Scene]:
        _ensure_unique([item.id for item in value], "scene")
        return value

    @field_validator("captions")
    @classmethod
    def unique_caption_ids(cls, value: list[Caption]) -> list[Caption]:
        _ensure_unique([item.id for item in value], "caption")
        return value

    @field_validator("audio_tracks")
    @classmethod
    def unique_audio_ids(cls, value: list[AudioTrack]) -> list[AudioTrack]:
        _ensure_unique([item.id for item in value], "audio track")
        return value


def _ensure_unique(ids: list[str], label: str) -> None:
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise ValueError(f"duplicate {label} id(s): {', '.join(duplicates)}")
