from open_download_api.core.exceptions import DownloadError, UnsupportedPlatformError
from open_download_api.core.platform_detector import platform_detector
from open_download_api.jobs import job_store
from open_download_api.mappers.media_info import MediaKind
from open_download_api.tasks.celery_app import celery_app

@celery_app.task
def run_download_job(job_id: str, url: str, kind: str) -> None:
    job_store.mark_running(job_id)
    try:
        downloader = platform_detector.detect(url)
        result = downloader.download(url, MediaKind(kind), job_id)
    except (UnsupportedPlatformError, DownloadError) as exc:
        job_store.mark_failed(job_id, str(exc))
        return

    job_store.mark_finished(job_id, result.files)
