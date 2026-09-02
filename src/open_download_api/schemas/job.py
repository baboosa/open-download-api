from enum import Enum
from pydantic import BaseModel

from open_download_api.mappers.media_info import DownloadedFile, MediaKind

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"

class Job(BaseModel):
    job_id: str
    status: JobStatus
    kind: MediaKind
    files: list[DownloadedFile] = []
    error_message: str | None = None
