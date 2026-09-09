from open_download_api.core.exceptions import DownloadError, UnsupportedPlatformError
from open_download_api.core.platform_detector import platform_detector
from open_download_api.core.ytdlp_errors import is_retryable_error
from open_download_api.jobs import job_store
from open_download_api.mappers.media_info import (
    DownloadedFile,
    FailedDownload,
    MediaKind,
)
from open_download_api.tasks.celery_app import celery_app


@celery_app.task
def run_download_job(job_id: str, urls: list[str], kind: str) -> None:
    job_store.mark_running(job_id)

    for url in urls:
        try:
            downloader = platform_detector.detect(url)
            result = downloader.download(url, MediaKind(kind), job_id)
            for file in result.files:
                job_store.record_success(job_id, file)
        except (UnsupportedPlatformError, DownloadError) as exc:
            message = str(exc)
            failed_item = FailedDownload(
                url=url, error_message=message, retryable=is_retryable_error(message)
            )
            job_store.record_failure(job_id, failed_item)

    job_store.finalize(job_id)
