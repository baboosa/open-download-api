import uuid

from fastapi import APIRouter, BackgroundTasks, status

from open_download_api.core.exceptions import DownloadError, UnsupportedPlatformError
from open_download_api.core.platform_detector import platform_detector
from open_download_api.jobs.job_store import job_store
from open_download_api.mappers.media_info import MediaKind
from open_download_api.schemas.download import DownloadJobResponse, DownloadRequest
from open_download_api.schemas.job import JobStatus

router = APIRouter()

def _run_download_job(job_id: str, url: str, kind: MediaKind) -> None:
    job_store.mark_running(job_id)
    try:
        downloader = platform_detector.detect(url)
        result = downloader.download(url, kind, job_id)
    except (UnsupportedPlatformError, DownloadError) as exc:
        job_store.mark_failed(job_id, str(exc))
        return

    job_store.mark_finished(job_id, result.files)

@router.post("/download", status_code=status.HTTP_202_ACCEPTED, response_model=DownloadJobResponse)
def create_download(payload: DownloadRequest, background_tasks: BackgroundTasks) -> DownloadJobResponse:
    url = str(payload.url)
    job_id = uuid.uuid4().hex

    job_store.create(job_id, payload.kind)
    background_tasks.add_task(_run_download_job, job_id, url, payload.kind)

    return DownloadJobResponse(job_id=job_id, status=JobStatus.QUEUED, kind=payload.kind)
