from enum import Enum

from pydantic import BaseModel, Field

from open_download_api.mappers.media_info import (
    DownloadedFile,
    FailedDownload,
    MediaKind,
)


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"

class Job(BaseModel):
    job_id: str
    status: JobStatus
    kind: MediaKind
    total_items: int = Field(default=0, description="Total number of items in this job")
    processed_items: int = Field(
        default=0, description="Items attempted so far, regardless of outcome"
    )
    files: list[DownloadedFile] = Field(default=[], description="Successfully downloaded items")
    failed: list[FailedDownload] = Field(default=[], description="Items that failed, if any")
    error_message: str | None = Field(default=None, description="Populated only when every item failed")
