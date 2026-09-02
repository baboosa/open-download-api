import uuid

from fastapi import APIRouter, status, HTTPException

from open_download_api.core.exceptions import DownloadError, UnsupportedPlatformError
from open_download_api.core.platform_detector import platform_detector
from open_download_api.schemas.download import DownloadJobResponse, DownloadRequest

router = APIRouter()

@router.post("/download", status_code=status.HTTP_202_ACCEPTED, response_model=DownloadJobResponse)
def create_download(payload: DownloadRequest) -> DownloadJobResponse:
    url = str(payload.url)

    try:
        downloader = platform_detector.detect(url)
    except UnsupportedPlatformError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        result = downloader.download(url, payload.kind)
    except DownloadError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    job_id = uuid.uuid4().hex
    return DownloadJobResponse(
        job_id=job_id,
        status="completed",
        kind=result.kind,
        file_name=result.file_name,
    )
