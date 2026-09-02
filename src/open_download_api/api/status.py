from fastapi import APIRouter

from open_download_api.schemas.status import JobStatusResponse

router = APIRouter()

@router.get("/status/{job_id}", response_model=JobStatusResponse)
def get_status(job_id: str) -> JobStatusResponse:
    return JobStatusResponse(job_id=job_id, status="queued")