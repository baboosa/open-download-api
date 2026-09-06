from enum import Enum
from pydantic import BaseModel, Field

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
    files: list[DownloadedFile] = Field(
        default=[], description="Populated only when status is 'finished'"
    )
    error_message: str | None = Field(
        default=None, description="Populated only when status is 'failed'"
    )
