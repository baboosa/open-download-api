from enum import Enum

from pydantic import BaseModel

class MediaKind(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"

class VideoInfo(BaseModel):
    title: str
    duration_seconds: int
    source_url: str

class DownloadedFile(BaseModel):
    file_name: str
    file_path: str

class DownloadResult(BaseModel):
    kind: MediaKind
    files: list[DownloadedFile]
