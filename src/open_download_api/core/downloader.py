from abc import ABC, abstractmethod

from open_download_api.mappers.media_info import DownloadResult, MediaKind, VideoInfo

class Downloader(ABC):
    @abstractmethod
    def matches(self, url: str) -> bool:
        ...

    @abstractmethod
    def fetch_info(self, url: str) -> list[VideoInfo]:
        ...

    @abstractmethod
    def download(self, url: str, kind: MediaKind) -> DownloadResult:
        ...