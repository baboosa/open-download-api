from open_download_api.jobs.in_memory_job_store import InMemoryJobStore
from open_download_api.jobs.job_store import JobStore

job_store: JobStore = InMemoryJobStore()
