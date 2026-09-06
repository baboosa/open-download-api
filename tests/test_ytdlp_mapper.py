from open_download_api.mappers.media_info import VideoInfo
from open_download_api.mappers.ytdlp_mapper import YtDlpMapper

def test_map_one_extracts_expected_fields():
    raw = {
        "title": "Test video",
        "duration": 213,
        "webpage_url": "https://youtube.com/watch?v=abc",
    }

    result = YtDlpMapper.map_one(raw)

    assert result == VideoInfo(
        title="Test video",
        duration_seconds=213,
        source_url="https://youtube.com/watch?v=abc",
    )


def test_map_one_uses_fallback_when_fields_are_missing():
    result = YtDlpMapper.map_one({})

    assert result.title == "Not title"
    assert result.duration_seconds == 0
    assert result.source_url == ""


def test_map_many_returns_single_item_for_regular_video():
    raw = {"title": "Video 1", "duration": 100, "webpage_url": "https://x.com"}

    result = YtDlpMapper.map_many(raw)

    assert len(result) == 1
    assert result[0].title == "Video 1"


def test_map_many_returns_all_entries_for_playlist():
    raw = {
        "_type": "playlist",
        "entries": [
            {"title": "Item 1", "duration": 10, "webpage_url": "https://x.com/1"},
            {"title": "Item 2", "duration": 20, "webpage_url": "https://x.com/2"},
        ],
    }

    result = YtDlpMapper.map_many(raw)

    assert len(result) == 2
    assert result[0].title == "Item 1"
    assert result[1].title == "Item 2"
