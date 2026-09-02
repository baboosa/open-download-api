from enum import Enum

from pydantic import BaseModel

class MediaKind(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"

class VideoInfo(BaseModel):
    title: str
    duration_seconds: int
    source_url: str

class DownloadResult(BaseModel):
    file_path: str
    file_name: str
    kind: MediaKind
