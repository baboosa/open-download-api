from open_download_api.jobs.job_store import JobStore
from open_download_api.mappers.media_info import (
    DownloadedFile,
    FailedDownload,
    MediaKind,
)
from open_download_api.schemas.job import Job, JobStatus


class InMemoryJobStore(JobStore):
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def create(self, job_id: str, kind: MediaKind, total_items: int) -> Job:
        job = Job(job_id=job_id, status=JobStatus.QUEUED, kind=kind, total_items=total_items)
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def mark_running(self, job_id: str) -> None:
        self._jobs[job_id].status = JobStatus.RUNNING

    def record_success(self, job_id: str, file: DownloadedFile) -> None:
        job = self._jobs[job_id]
        job.files.append(file)
        job.processed_items += 1

    def record_failure(self, job_id: str, failed: FailedDownload) -> None:
        job = self._jobs[job_id]
        job.failed.append(failed)
        job.processed_items += 1

    def finalize(self, job_id: str) -> None:
        job = self._jobs[job_id]
        if job.files:
            job.status = JobStatus.FINISHED
            job.error_message = None
        else:
            job.status = JobStatus.FAILED
            job.error_message = f"All {len(job.failed)} item(s) failed to download"

    def reset_for_retry(self, job_id: str, kept_failed: list[FailedDownload], processed_items: int) -> None:
        job = self._jobs[job_id]
        job.status = JobStatus.QUEUED
        job.processed_items = processed_items
        job.failed = kept_failed
        job.error_message = None
