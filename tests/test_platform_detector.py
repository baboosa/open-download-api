import pytest

from open_download_api.core.downloader import Downloader
from open_download_api.core.exceptions import UnsupportedPlatformError
from open_download_api.core.platform_detector import PlatformDetector
from open_download_api.mappers.media_info import DownloadResult, MediaKind, VideoInfo


class DummyDownloader(Downloader):
    def matches(self, url: str) -> bool:
        return "example.com" in url

    def fetch_info(self, url: str) -> list[VideoInfo]:
        return []

    def download(self, url: str, kind: MediaKind, job_id: str) -> DownloadResult:
        return DownloadResult(kind=kind, files=[])

def test_detect_returns_matching_strategy():
    detector = PlatformDetector([DummyDownloader()])

    result = detector.detect("https://example.com/video")

    assert isinstance(result, DummyDownloader)

def test_detect_raises_when_no_strategy_matches():
    detector = PlatformDetector([DummyDownloader()])

    with pytest.raises(UnsupportedPlatformError):
        detector.detect("https://outra-plataforma.com/video")
