from pydantic import BaseModel, HttpUrl, Field

from open_download_api.mappers.media_info import VideoInfo

class ExtractInfoRequest(BaseModel):
    url: HttpUrl = Field(
        description="YouTube video or playlist URL",
        examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
    )

class ExtractInfoResponse(BaseModel):
    items: list[VideoInfo] = Field(
        description="One entry per video (a single item for regular videos, multiple for playlists)"
    )