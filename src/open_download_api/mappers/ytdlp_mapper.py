from typing import Any

from open_download_api.mappers.media_info import VideoInfo

RawInfo = dict[str, Any]
MAX_PLAYLIST_ITEMS = 15
PLAYLIST_ITEMS_RANGE = f"1-{MAX_PLAYLIST_ITEMS}"

class YtDlpMapper:
    @staticmethod
    def map_one(raw: RawInfo) -> VideoInfo:
        return VideoInfo(
            title=raw.get("title", "Not title"),
            duration_seconds=raw.get("duration") or 0,
            source_url=raw.get("webpage_url") or raw.get("url", ""),
        )

    @staticmethod
    def map_many(raw: dict) -> list[VideoInfo]:
        entries = YtDlpMapper.extract_entries(raw)
        return [YtDlpMapper.map_one(entry) for entry in entries]

    @staticmethod
    def extract_entries(raw: dict) -> list[dict]:
        if raw.get("_type") == "playlist":
            return raw.get("entries", [])
        return [raw]