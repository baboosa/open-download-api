from pydantic import BaseModel, HttpUrl, Field

from open_download_api.mappers.media_info import MediaKind
from open_download_api.schemas.job import JobStatus

class DownloadRequest(BaseModel):
    url: HttpUrl = Field(
        description="YouTube video or playlist URL",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )
    kind: MediaKind = Field(description="Whether to download as video or extract audio only")

class DownloadJobResponse(BaseModel):
    job_id: str = Field(description="Use this id to poll GET /status/{job_id}")
    status: JobStatus
    kind: MediaKind
