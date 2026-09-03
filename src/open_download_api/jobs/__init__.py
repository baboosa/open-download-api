from open_download_api.jobs.job_store import JobStore
from open_download_api.jobs.redis_job_store import RedisJobStore

job_store: JobStore = RedisJobStore()
