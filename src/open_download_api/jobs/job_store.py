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
    def record_success(self, job_id: str, file: DownloadedFile) -> None:
        ...

    @abstractmethod
    def record_failure(self, job_id: str, failed: FailedDownload) -> None:
        ...

    @abstractmethod
    def finalize(self, job_id: str) -> None:
        ...

    @abstractmethod
    def reset_for_retry(self, job_id: str, kept_failed: list[FailedDownload], processed_items: int) -> None:
        ...
