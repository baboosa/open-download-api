from fastapi import APIRouter, HTTPException

from open_download_api.jobs import job_store
from open_download_api.schemas.job import Job

router = APIRouter()

@router.get(
    "/status/{job_id}",
    response_model=Job,
    summary="Check a download job's status",
)
def get_status(job_id: str) -> Job:
    """
       Returns the current status of a job: queued, running, finished, or failed.
       Poll this endpoint after calling POST /download.
       """
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job