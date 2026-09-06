import pytest

from open_download_api.jobs.in_memory_job_store import InMemoryJobStore
from open_download_api.mappers.media_info import (
    DownloadedFile,
    FailedDownload,
    MediaKind,
)
from open_download_api.schemas.job import JobStatus


@pytest.fixture
def store() -> InMemoryJobStore:
    return InMemoryJobStore()

def test_create_stores_job_with_queued_status(store: InMemoryJobStore):
    job = store.create("job-1", MediaKind.AUDIO, total_items=1)

    assert job.status == JobStatus.QUEUED
    assert job.kind == MediaKind.AUDIO

def test_get_returns_none_for_unknown_job(store: InMemoryJobStore):
    assert store.get("does-not-exist") is None

def test_mark_finished_updates_status_and_files(store: InMemoryJobStore):
    store.create("job-1", MediaKind.VIDEO, total_items=1)

    files = [DownloadedFile(file_name="a.mp4", file_path="/media/job-1/a.mp4")]
    store.mark_finished("job-1", files, [])

    job = store.get("job-1")
    assert job.status == JobStatus.FINISHED
    assert job.files == files

def test_mark_failed_updates_status_and_error_message(store: InMemoryJobStore):
    store.create("job-1", MediaKind.AUDIO, total_items=1)

    store.mark_failed("job-1", "something went wrong", [])

    job = store.get("job-1")
    assert job.status == JobStatus.FAILED
    assert job.error_message == "something went wrong"

def test_reset_for_retry_clears_failed_and_resets_status(store: InMemoryJobStore):
    store.create("job-1", MediaKind.AUDIO, total_items=1)
    store.mark_finished(
        "job-1",
        files=[DownloadedFile(file_name="a.mp3", file_path="/media/job-1/a.mp3")],
        failed=[FailedDownload(url="https://x.com/1", error_message="boom", retryable=True)],
    )

    store.reset_for_retry("job-1", processed_items=1)

    job = store.get("job-1")
    assert job.status == JobStatus.QUEUED
    assert job.processed_items == 1
    assert job.failed == []
    assert job.error_message is None


def test_reset_for_retry_preserves_previously_successful_files(store: InMemoryJobStore):
    store.create("job-1", MediaKind.AUDIO, total_items=1)
    files = [DownloadedFile(file_name="a.mp3", file_path="/media/job-1/a.mp3")]
    store.mark_finished("job-1", files=files, failed=[])

    store.reset_for_retry("job-1", processed_items=1)

    job = store.get("job-1")
    assert job.files == files
