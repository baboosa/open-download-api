import uuid
import zipfile
from pathlib import Path

from fastapi import APIRouter, status, HTTPException
from fastapi.responses import FileResponse

from open_download_api.core.exceptions import DownloadError, UnsupportedPlatformError
from open_download_api.core.platform_detector import platform_detector
from open_download_api.jobs import job_store
from open_download_api.mappers.media_info import MediaKind
from open_download_api.schemas.download import DownloadJobResponse, DownloadRequest
from open_download_api.schemas.job import JobStatus
from open_download_api.tasks.download_task import run_download_job

router = APIRouter()
MEDIA_DIR = Path("media")

@router.post(
    "/download",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=DownloadJobResponse,
    summary="Queue a video/playlist download",
)
def create_download(payload: DownloadRequest) -> DownloadJobResponse:
    """
       Queues a download job and returns immediately with a job_id.
       The actual download runs in the background via a Celery worker -
       poll GET /status/{job_id} to track progress.
    """
    url = str(payload.url)

    try:
        platform_detector.detect(url)
    except UnsupportedPlatformError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    job_id = uuid.uuid4().hex

    job_store.create(job_id, payload.kind)
    run_download_job.delay(job_id, url, payload.kind.value)

    return DownloadJobResponse(job_id=job_id, status=JobStatus.QUEUED, kind=payload.kind)

@router.get(
    "/download/{job_id}/file",
    summary="Download the finished file(s) as a zip",
)
def get_download_file(job_id: str) -> FileResponse:
    """
    Returns a zip archive containing all downloaded files for this job.
    Only available once the job's status is 'finished'.
    """
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.FINISHED:
        raise HTTPException(status_code=409, detail=f"Job is not finished (status={job.status.value})")

    if not job.files:
        raise HTTPException(status_code=404, detail="No files found for this job")

    zip_path = _build_zip(job_id, job.files)
    return FileResponse(path=zip_path, filename=zip_path.name, media_type="application/zip")


def _build_zip(job_id: str, files: list) -> Path:
    job_dir = MEDIA_DIR / job_id
    zip_path = job_dir / "download.zip"

    if zip_path.exists():
        return zip_path

    with zipfile.ZipFile(zip_path, "w") as zip_file:
        for downloaded_file in files:
            zip_file.write(downloaded_file.file_path, arcname=downloaded_file.file_name)

    return zip_path

def _run_download_job(job_id: str, url: str, kind: MediaKind) -> None:
    job_store.mark_running(job_id)
    try:
        downloader = platform_detector.detect(url)
        result = downloader.download(url, kind, job_id)
    except (UnsupportedPlatformError, DownloadError) as exc:
        job_store.mark_failed(job_id, str(exc))
        return

    job_store.mark_finished(job_id, result.files)
