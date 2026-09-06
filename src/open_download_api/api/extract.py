from fastapi import APIRouter, HTTPException

from open_download_api.core.exceptions import ExtractionError, UnsupportedPlatformError
from open_download_api.core.platform_detector import platform_detector
from open_download_api.schemas.extract import ExtractInfoRequest, ExtractInfoResponse

router = APIRouter()

@router.post(
    "/extract-info",
    response_model=ExtractInfoResponse,
    summary="Extract metadata from a video or playlist",
)
def extract_info(payload: ExtractInfoRequest) -> ExtractInfoResponse:
    """
        Fetches metadata (title, duration, source URL) for a video or a
        playlist (limited to the first 15 items), without downloading anything.
    """
    url = str(payload.url)
    try:
        downloader = platform_detector.detect(url)
    except UnsupportedPlatformError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        items = downloader.fetch_info(url)
    except ExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ExtractInfoResponse(items=items)