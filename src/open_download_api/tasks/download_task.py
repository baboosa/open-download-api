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

    new_files: list[DownloadedFile] = []
    new_failed: list[FailedDownload] = []

    for url in urls:
        try:
            downloader = platform_detector.detect(url)
            result = downloader.download(url, MediaKind(kind), job_id)
            new_files.extend(result.files)
        except (UnsupportedPlatformError, DownloadError) as exc:
            message = str(exc)
            new_failed.append(
                FailedDownload(url=url, error_message=message, retryable=is_retryable_error(message))
            )
        finally:
            job_store.increment_progress(job_id)

    existing_job = job_store.get(job_id)
    previous_files = existing_job.files if existing_job else []
    previous_non_retryable = (
        [f for f in existing_job.failed if not f.retryable] if existing_job else []
    )

    combined_files = previous_files + new_files
    combined_failed = previous_non_retryable + new_failed

    if combined_files:
        job_store.mark_finished(job_id, combined_files, combined_failed)
    else:
        summary = f"All {len(combined_failed)} item(s) failed to download"
        job_store.mark_failed(job_id, summary, combined_failed)
