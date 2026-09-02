import uuid, yt_dlp

from pathlib import Path
from yt_dlp.utils import DownloadError as YtDlpDownloadError
from typing import TypedDict, NotRequired, Literal

from open_download_api.core.downloader import Downloader
from open_download_api.core.exceptions import DownloadError, ExtractionError
from open_download_api.mappers.media_info import DownloadResult, MediaKind, VideoInfo
from open_download_api.mappers.ytdlp_mapper import YtDlpMapper
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
    noplaylist: bool
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
            "playlist_items": "1-50",
        }
        try:
            with yt_dlp.YoutubeDL(dict(options)) as ydl:  # type: ignore[arg-type]
                raw = ydl.extract_info(url, download=False)
        except YtDlpDownloadError as exc:
            raise ExtractionError(f"Could not extract metadata: {exc}") from exc

        return YtDlpMapper.map_many(raw)

    def download(self, url: str, kind: MediaKind) -> DownloadResult:
        MEDIA_DIR.mkdir(parents=True, exist_ok=True)
        file_id = uuid.uuid4().hex
        options = self._build_download_options(file_id, kind)

        raw_info = self._run_download(url, options)
        print("raw infooo", raw_info)
        slug = slugify(raw_info.get("title", "media"))

        result_file = self._find_downloaded_file(file_id)
        final_path = result_file.with_stem(f"{slug}-{file_id[:8]}")
        result_file.rename(final_path)

        return DownloadResult(
            file_path=str(result_file),
            file_name=final_path.name,
            kind=kind,
        )

    @staticmethod
    def _build_download_options(file_id: str, kind: MediaKind) -> YtDlpOptions:
        output_template = str(MEDIA_DIR / f"{file_id}.%(ext)s")
        content_format = AUDIO_FORMAT_SELECTOR if kind == MediaKind.AUDIO else VIDEO_FORMAT_SELECTOR

        options: YtDlpOptions = {
            "outtmpl": output_template,
            "noplaylist": True,
            "format": content_format
        }

        if kind == MediaKind.AUDIO:
            postprocessor: YtDlpPostprocessor = {
                "key": POSTPROCESSOR_EXTRACT_AUDIO,
                "preferredcodec": AUDIO_CODEC
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