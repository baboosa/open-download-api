from fastapi import APIRouter, HTTPException

from open_download_api.jobs import job_store
from open_download_api.schemas.job import Job

router = APIRouter()

@router.get("/status/{job_id}", response_model=Job)
def get_status(job_id: str) -> Job:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job