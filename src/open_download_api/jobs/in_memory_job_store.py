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

    def mark_finished(self, job_id: str, files: list[DownloadedFile], failed: list[FailedDownload]) -> None:
        self._jobs[job_id].status = JobStatus.FINISHED
        self._jobs[job_id].files = files
        self._jobs[job_id].failed = failed

    def mark_failed(self, job_id: str, error_message: str, failed: list[FailedDownload]) -> None:
        self._jobs[job_id].status = JobStatus.FAILED
        self._jobs[job_id].error_message = error_message
        self._jobs[job_id].failed = failed

    def increment_progress(self, job_id: str) -> None:
        self._jobs[job_id].processed_items += 1

    def reset_for_retry(self, job_id: str, processed_items: int) -> None:
        job = self._jobs[job_id]
        job.status = JobStatus.QUEUED
        job.processed_items = processed_items
        job.failed = []
        job.error_message = None
