"""ASS subtitle generation with Unicode support."""

from pathlib import Path

from .models import Caption, StyleConfig


def ass_time(seconds: float) -> str:
    centiseconds = max(0, round(seconds * 100))
    hours, remainder = divmod(centiseconds, 360000)
    minutes, remainder = divmod(remainder, 6000)
    secs, fraction = divmod(remainder, 100)
    return f"{hours}:{minutes:02d}:{secs:02d}.{fraction:02d}"


def escape_ass_text(text: str) -> str:
    """Escape control syntax while retaining Vietnamese Unicode text."""
    return (
        text.replace("\\", r"\\")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("\r\n", r"\N")
        .replace("\n", r"\N")
    )


def _ass_color(value: str) -> str:
    red, green, blue = value[1:3], value[3:5], value[5:7]
    return f"&H00{blue}{green}{red}"


def render_ass(captions: list[Caption], style: StyleConfig, width: int, height: int) -> str:
    alignment = {"bottom_center": 2, "center": 5, "top_center": 8}
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,{style.font_name},{style.font_size},{_ass_color(style.primary_color)},&H000000FF,{_ass_color(style.outline_color)},&H80000000,-1,0,0,0,100,100,0,0,1,{style.outline_width},{style.shadow},{alignment[style.alignment.value]},{style.margin_left},{style.margin_right},{style.margin_bottom},1

[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    events = []
    for caption in captions:
        override = rf"{{\an{alignment[caption.position.value]}}}"
        events.append(
            f"Dialogue: 0,{ass_time(caption.start)},{ass_time(caption.end)},Default,,0,0,0,,"
            f"{override}{escape_ass_text(caption.text)}"
        )
    return header + "\n".join(events) + ("\n" if events else "")


def write_ass(path: Path, captions: list[Caption], style: StyleConfig, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_ass(captions, style, width, height), encoding="utf-8-sig")
