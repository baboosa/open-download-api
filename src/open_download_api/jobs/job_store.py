from abc import ABC, abstractmethod

from open_download_api.mappers.media_info import DownloadedFile, MediaKind
from open_download_api.schemas.job import Job

class JobStore(ABC):
    @abstractmethod
    def create(self, job_id: str, kind: MediaKind) -> Job:
        ...

    @abstractmethod
    def get(self, job_id: str) -> Job | None:
        ...

    @abstractmethod
    def mark_running(self, job_id: str) -> None:
        ...

    @abstractmethod
    def mark_finished(self, job_id: str, files: list[DownloadedFile]) -> None:
        ...

    @abstractmethod
    def mark_failed(self, job_id: str, error_message: str) -> None:
        ...
