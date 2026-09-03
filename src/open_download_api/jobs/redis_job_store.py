import redis

from open_download_api.jobs.job_store import JobStore
from open_download_api.mappers.media_info import DownloadedFile, MediaKind
from open_download_api.schemas.job import Job, JobStatus

JOB_TTL_SECONDS = 60 * 60 * 24  # 24 hours

class RedisJobStore(JobStore):
    def __init__(self, host: str = "localhost", port: int = 6379) -> None:
        self._redis = redis.Redis(host=host, port=port, decode_responses=True)

    def create(self, job_id: str, kind: MediaKind) -> Job:
        job = Job(job_id=job_id, status=JobStatus.QUEUED, kind=kind)
        self._save(job)
        return job

    def get(self, job_id: str) -> Job | None:
        raw = self._redis.get(self._key(job_id))
        if raw is None:
            return None
        return Job.model_validate_json(raw)

    def mark_running(self, job_id: str) -> None:
        job = self._require(job_id)
        job.status = JobStatus.RUNNING
        self._save(job)

    def mark_finished(self, job_id: str, files: list[DownloadedFile]) -> None:
        job = self._require(job_id)
        job.status = JobStatus.FINISHED
        job.files = files
        self._save(job)

    def mark_failed(self, job_id: str, error_message: str) -> None:
        job = self._require(job_id)
        job.status = JobStatus.FAILED
        job.error_message = error_message
        self._save(job)

    def _require(self, job_id: str) -> Job:
        job = self.get(job_id)
        if job is None:
            raise KeyError(f"Job {job_id} not found")
        return job

    def _save(self, job: Job) -> None:
        self._redis.set(self._key(job.job_id), job.model_dump_json(), ex=JOB_TTL_SECONDS)

    @staticmethod
    def _key(job_id: str) -> str:
        return f"job:{job_id}"
