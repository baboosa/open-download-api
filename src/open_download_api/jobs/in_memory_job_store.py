from open_download_api.jobs.job_store import JobStore
from open_download_api.mappers.media_info import DownloadedFile, MediaKind
from open_download_api.schemas.job import Job, JobStatus

class InMemoryJobStore(JobStore):
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def create(self, job_id: str, kind: MediaKind) -> Job:
        job = Job(job_id=job_id, status=JobStatus.QUEUED, kind=kind)
        self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def mark_running(self, job_id: str) -> None:
        self._jobs[job_id].status = JobStatus.RUNNING

    def mark_finished(self, job_id: str, files: list[DownloadedFile]) -> None:
        self._jobs[job_id].status = JobStatus.FINISHED
        self._jobs[job_id].files = files

    def mark_failed(self, job_id: str, error_message: str) -> None:
        self._jobs[job_id].status = JobStatus.FAILED
        self._jobs[job_id].error_message = error_message
