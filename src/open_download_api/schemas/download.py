from pydantic import BaseModel, HttpUrl

from open_download_api.mappers.media_info import MediaKind
from open_download_api.schemas.job import JobStatus

class DownloadRequest(BaseModel):
    url: HttpUrl
    kind: MediaKind

class DownloadJobResponse(BaseModel):
    job_id: str
    status: JobStatus
    kind: MediaKind
