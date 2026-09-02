from typing import Any

from open_download_api.mappers.media_info import VideoInfo

RawInfo = dict[str, Any]

class YtDlpMapper:
    @staticmethod
    def map_one(raw: RawInfo) -> VideoInfo:
        return VideoInfo(
            title=raw.get("title", "Not title"),
            duration_seconds=raw.get("duration") or 0,
            source_url=raw.get("webpage_url") or raw.get("url", ""),
        )

    @staticmethod
    def map_many(raw: RawInfo) -> list[VideoInfo]:
        if raw.get("_type") == "playlist":
            entries = raw.get("entries", [])
            return [YtDlpMapper.map_one(entry) for entry in entries]

        return [YtDlpMapper.map_one(raw)]
