from enum import Enum

from pydantic import BaseModel, Field


class MediaKind(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"

class VideoInfo(BaseModel):
    title: str = Field(description="Video title", examples=["Rick Astley - Never Gonna Give You Up"])
    duration_seconds: int = Field(description="Video duration, in seconds", examples=[213])
    source_url: str = Field(description="Canonical URL of this specific video")

class DownloadedFile(BaseModel):
    file_name: str
    file_path: str

class DownloadResult(BaseModel):
    kind: MediaKind
    files: list[DownloadedFile]
