from fastapi import APIRouter, HTTPException

from open_download_api.core.exceptions import ExtractionError, UnsupportedPlatformError
from open_download_api.core.exceptions import UnsupportedPlatformError
from open_download_api.core.platform_detector import platform_detector
from open_download_api.schemas.extract import ExtractInfoRequest, ExtractInfoResponse

router = APIRouter()

@router.post("/extract-info", response_model=ExtractInfoResponse)
def extract_info(payload: ExtractInfoRequest) -> ExtractInfoResponse:
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