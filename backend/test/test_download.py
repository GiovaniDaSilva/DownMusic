from src.pipeline.download import extract_video_id


def test_extract_video_id():
    vid = "dQw4w9WgXcQ"
    assert extract_video_id(f"https://www.youtube.com/watch?v={vid}") == vid
    assert extract_video_id(f"https://youtu.be/{vid}?t=10") == vid
    assert extract_video_id(f"https://youtube.com/shorts/{vid}") == vid
    assert extract_video_id(f"https://music.youtube.com/watch?v={vid}&list=x") == vid
    assert extract_video_id("https://example.com") is None
