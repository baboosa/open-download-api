import uuid, yt_dlp

from pathlib import Path
from yt_dlp.utils import DownloadError as YtDlpDownloadError
from typing import TypedDict, NotRequired, Literal

from open_download_api.core.downloader import Downloader
from open_download_api.core.exceptions import DownloadError, ExtractionError
from open_download_api.mappers.media_info import DownloadResult, MediaKind, VideoInfo, DownloadedFile
from open_download_api.mappers.ytdlp_mapper import YtDlpMapper, PLAYLIST_ITEMS_RANGE
from open_download_api.utils.text import slugify

PostprocessorKey = Literal["FFmpegExtractAudio"]
AudioCodec = Literal["mp3"]

MEDIA_DIR = Path("media")
AUDIO_FORMAT_SELECTOR = "bestaudio/best"
VIDEO_FORMAT_SELECTOR = "bestvideo+bestaudio/best"
AUDIO_CODEC = "mp3"
VIDEO_CONTAINER = "mp4"
POSTPROCESSOR_EXTRACT_AUDIO = "FFmpegExtractAudio"

class YtDlpPostprocessor(TypedDict):
    key: PostprocessorKey
    preferredcodec: AudioCodec

class YtDlpOptions(TypedDict):
    outtmpl: str
    playlist_items: str
    format: str
    merge_output_format: NotRequired[str]
    postprocessors: NotRequired[list[YtDlpPostprocessor]]

class YoutubeDownloader(Downloader):
    def matches(self, url: str) -> bool:
        return "youtube.com" in url or "youtu.be" in url

    def fetch_info(self, url: str) -> list[VideoInfo]:
        options = {
            "skip_download": True,
            "socket_timeout": 10,
            "extractor_retries": 1,
            "playlist_items": PLAYLIST_ITEMS_RANGE,
        }
        try:
            with yt_dlp.YoutubeDL(dict(options)) as ydl:  # type: ignore[arg-type]
                raw = ydl.extract_info(url, download=False)
        except YtDlpDownloadError as exc:
            raise ExtractionError(f"Could not extract metadata: {exc}") from exc

        return YtDlpMapper.map_many(dict(raw))

    def download(self, url: str, kind: MediaKind, job_id: str) -> DownloadResult:
        job_dir = MEDIA_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        options = self._build_download_options(job_dir, kind)
        raw = self._run_download(url, options)

        entries = YtDlpMapper.extract_entries(raw)
        files = [self._rename_entry_output(job_dir, entry) for entry in entries]

        return DownloadResult(kind=kind, files=files)

    @staticmethod
    def _build_download_options(job_dir: Path, kind: MediaKind) -> YtDlpOptions:
        output_template = str(job_dir / "%(id)s.%(ext)s")
        content_format = AUDIO_FORMAT_SELECTOR if kind == MediaKind.AUDIO else VIDEO_FORMAT_SELECTOR

        options: YtDlpOptions = {
            "outtmpl": output_template,
            "playlist_items": PLAYLIST_ITEMS_RANGE,
            "format": content_format,
        }

        if kind == MediaKind.AUDIO:
            postprocessor: YtDlpPostprocessor = {
                "key": POSTPROCESSOR_EXTRACT_AUDIO,
                "preferredcodec": AUDIO_CODEC,
            }
            options["postprocessors"] = [postprocessor]
        else:
            options["merge_output_format"] = VIDEO_CONTAINER

        return options

    @staticmethod
    def _run_download(url: str, options: YtDlpOptions) -> dict:
        try:
            with yt_dlp.YoutubeDL(dict(options)) as ydl:  # type: ignore[arg-type]
                raw = ydl.extract_info(url)
                return dict(raw)
        except YtDlpDownloadError as exc:
            raise DownloadError(f"Could not download media: {exc}") from exc

    @staticmethod
    def _find_downloaded_file(file_id: str) -> Path:
        matches = list(MEDIA_DIR.glob(f"{file_id}.*"))
        if not matches:
            raise DownloadError("Download finished but output file was not found")
        return matches[0]

    @staticmethod
    def _rename_entry_output(job_dir: Path, entry: dict) -> DownloadedFile:
        video_id = entry.get("id")
        matches = list(job_dir.glob(f"{video_id}.*"))
        if not matches:
            raise DownloadError(f"Downloaded file not found for id {video_id}")

        original_file = matches[0]
        slug = slugify(entry.get("title", "media"))
        final_path = original_file.with_stem(f"{slug}-{video_id[:8]}")
        original_file.rename(final_path)

        return DownloadedFile(file_name=final_path.name, file_path=str(final_path))
