import redis

from open_download_api.jobs.job_store import JobStore
from open_download_api.mappers.media_info import (
    DownloadedFile,
    FailedDownload,
    MediaKind,
)
from open_download_api.schemas.job import Job, JobStatus
from open_download_api.settings import settings

JOB_TTL_SECONDS = 60 * 60 * 24  # 24 hours

class RedisJobStore(JobStore):
    def __init__(self) -> None:
        self._redis = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.job_store_redis_db,
            decode_responses=True,
        )

    def create(self, job_id: str, kind: MediaKind, total_items: int) -> Job:
        job = Job(job_id=job_id, status=JobStatus.QUEUED, kind=kind, total_items=total_items)
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

    def record_success(self, job_id: str, file: DownloadedFile) -> None:
        job = self._require(job_id)
        job.files.append(file)
        job.processed_items += 1
        self._save(job)

    def record_failure(self, job_id: str, failed: FailedDownload) -> None:
        job = self._require(job_id)
        job.failed.append(failed)
        job.processed_items += 1
        self._save(job)

    def finalize(self, job_id: str) -> None:
        job = self._require(job_id)
        if job.files:
            job.status = JobStatus.FINISHED
            job.error_message = None
        else:
            job.status = JobStatus.FAILED
            job.error_message = f"All {len(job.failed)} item(s) failed to download"
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

    def reset_for_retry(self, job_id: str, processed_items: int) -> None:
        job = self._require(job_id)
        job.status = JobStatus.QUEUED
        job.processed_items = processed_items
        job.failed = []
        job.error_message = None
        self._save(job)