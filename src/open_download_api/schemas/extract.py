from pydantic import BaseModel, HttpUrl

from open_download_api.mappers.media_info import VideoInfo

class ExtractInfoRequest(BaseModel):
    url: HttpUrl


class ExtractInfoResponse(BaseModel):
    items: list[VideoInfo]