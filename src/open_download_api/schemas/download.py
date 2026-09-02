from pydantic import BaseModel, HttpUrl

from open_download_api.mappers.media_info import MediaKind

class DownloadRequest(BaseModel):
    url: HttpUrl
    kind: MediaKind

class DownloadJobResponse(BaseModel):
    job_id: str
    status: str
    kind: MediaKind
    file_name: str
