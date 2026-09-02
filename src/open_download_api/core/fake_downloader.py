from open_download_api.core.downloader import Downloader

class FakeDownloader(Downloader):
    def matches(self, url: str) -> bool:
        return "youtube.com" in url or "youtu.be" in url

    def fetch_info(self, url: str) -> dict:
        return {
            "title": "Example video (YouTube)",
            "duration_seconds": 213,
            "source_url": url,
        }