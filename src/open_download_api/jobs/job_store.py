from abc import ABC, abstractmethod

from open_download_api.mappers.media_info import (
    DownloadedFile,
    FailedDownload,
    MediaKind,
)
from open_download_api.schemas.job import Job


class JobStore(ABC):
    @abstractmethod
    def create(self, job_id: str, kind: MediaKind, total_items: int) -> Job:
        ...

    @abstractmethod
    def get(self, job_id: str) -> Job | None:
        ...

    @abstractmethod
    def mark_running(self, job_id: str) -> None:
        ...

    @abstractmethod
    def mark_finished(self, job_id: str, files: list[DownloadedFile], failed: list[FailedDownload]) -> None:
        ...

    @abstractmethod
    def mark_failed(self, job_id: str, error_message: str, failed: list[FailedDownload]) -> None:
        ...

    @abstractmethod
    def increment_progress(self, job_id: str) -> None:
        ...

    @abstractmethod
    def reset_for_retry(self, job_id: str, processed_items: int) -> None:
        ...
