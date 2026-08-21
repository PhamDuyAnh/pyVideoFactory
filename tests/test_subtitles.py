from video_factory.models import Caption, StyleConfig
from video_factory.subtitles import escape_ass_text, render_ass


def test_escape_vietnamese_and_ass_control():
    text = escape_ass_text("Tối nay: {DX}!\nNghe rõ")
    assert "Tối nay:" in text
    assert r"\{DX\}" in text
    assert r"\N" in text


def test_ass_contains_unicode_caption():
    output = render_ass([Caption(id="c", text="Có ai nghe không?", start=0, end=1)], StyleConfig(), 320, 568)
    assert "Có ai nghe không?" in output
    assert "Dialogue: 0,0:00:00.00,0:00:01.00" in output

