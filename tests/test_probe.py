from video_factory.probe import parse_probe_json


def test_parse_probe_json():
    info = parse_probe_json({"format": {"duration": "2.5"}, "streams": [{"codec_type": "video", "width": 320, "height": 568, "avg_frame_rate": "24/1", "codec_name": "h264", "pix_fmt": "yuv420p"}, {"codec_type": "audio", "sample_rate": "48000", "channels": 2}]})
    assert info.duration == 2.5
    assert info.has_video and info.has_audio
    assert info.fps == 24

