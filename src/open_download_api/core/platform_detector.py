from open_download_api.core.downloader import Downloader
from open_download_api.core.exceptions import UnsupportedPlatformError
from open_download_api.core.youtube_downloader import YoutubeDownloader

class PlatformDetector:
    def __init__(self, strategies: list[Downloader]):
        self._strategies = strategies

    def detect(self, url: str) -> Downloader:
        for strategy in self._strategies:
            print(url)
            if strategy.matches(url):
                return strategy
        raise UnsupportedPlatformError(f"No strategy supports this URL: {url}")

platform_detector = PlatformDetector([YoutubeDownloader()])
