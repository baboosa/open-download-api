from pydantic import BaseModel, Field, HttpUrl

from open_download_api.mappers.media_info import MediaKind
from open_download_api.schemas.job import JobStatus


class DownloadRequest(BaseModel):
    urls: list[HttpUrl] = Field(min_length=1, max_length=15)
    kind: MediaKind = Field(description="Whether to download as video or extract audio only")

class DownloadJobResponse(BaseModel):
    job_id: str = Field(description="Use this id to poll GET /status/{job_id}")
    status: JobStatus
    kind: MediaKind
