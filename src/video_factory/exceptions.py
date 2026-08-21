"""Application-specific exceptions."""


class VideoFactoryError(Exception):
    """Base error shown as a concise CLI message."""


class ConfigurationError(VideoFactoryError):
    """Project configuration cannot be loaded."""


class ProjectValidationError(VideoFactoryError):
    """Project media or configuration is invalid."""


class FFmpegMissingError(VideoFactoryError):
    """FFmpeg or ffprobe is unavailable."""


class ProbeError(VideoFactoryError):
    """ffprobe could not inspect a media file."""


class RenderError(VideoFactoryError):
    """A render stage failed."""

