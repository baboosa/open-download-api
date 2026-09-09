from enum import Enum

from pydantic import BaseModel, Field


class MediaKind(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"

class VideoInfo(BaseModel):
    title: str = Field(description="Video title", examples=["Rick Astley - Never Gonna Give You Up"])
    duration_seconds: int = Field(description="Video duration, in seconds", examples=[213])
    source_url: str = Field(description="Canonical URL of this specific video")
    thumbnail_url: str | None = Field(
        default=None, description="URL of the video's thumbnail image, if available"
    )

class DownloadedFile(BaseModel):
    file_name: str
    file_path: str
    file_size_bytes: int = Field(description="File size in bytes")

class DownloadResult(BaseModel):
    kind: MediaKind
    files: list[DownloadedFile]

class FailedDownload(BaseModel):
    url: str
    error_message: str
    retryable: bool = Field(default=True, description="Whether retrying this item might succeed")
