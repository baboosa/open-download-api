from pathlib import Path
from urllib.parse import urlparse

import yt_dlp
from yt_dlp.utils import DownloadError as YtDlpDownloadError

from open_download_api.core.downloader import Downloader
from open_download_api.core.exceptions import DownloadError, ExtractionError
from open_download_api.core.ytdlp_types import (
    AUDIO_CODEC,
    POSTPROCESSOR_EMBED_THUMBNAIL,
    POSTPROCESSOR_EXTRACT_AUDIO,
    POSTPROCESSOR_METADATA,
    EmbedThumbnailPostprocessor,
    FFmpegExtractAudioPostprocessor,
    FFmpegMetadataPostprocessor,
    YtDlpOptions,
)
from open_download_api.mappers.media_info import (
    DownloadedFile,
    DownloadResult,
    MediaKind,
    VideoInfo,
)
from open_download_api.mappers.ytdlp_mapper import PLAYLIST_ITEMS_RANGE, YtDlpMapper
from open_download_api.utils.text import slugify

MEDIA_DIR = Path("media")
AUDIO_FORMAT_SELECTOR = "bestaudio/best"
VIDEO_FORMAT_SELECTOR = "bestvideo+bestaudio/best"
VIDEO_CONTAINER = "mp4"

YOUTUBE_HOSTNAMES = {"www.youtube.com", "youtube.com", "music.youtube.com", "youtu.be"}

class YoutubeDownloader(Downloader):
    def matches(self, url: str) -> bool:
        hostname = urlparse(url).hostname or ""
        return hostname in YOUTUBE_HOSTNAMES

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
        files = [self._rename_entry_output(job_dir, entry, kind) for entry in entries]

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
            extract_audio: FFmpegExtractAudioPostprocessor = {
                "key": POSTPROCESSOR_EXTRACT_AUDIO,
                "preferredcodec": AUDIO_CODEC,
            }
            metadata: FFmpegMetadataPostprocessor = {"key": POSTPROCESSOR_METADATA}
            embed_thumbnail: EmbedThumbnailPostprocessor = {"key": POSTPROCESSOR_EMBED_THUMBNAIL}

            options["writethumbnail"] = True
            options["postprocessors"] = [extract_audio, metadata, embed_thumbnail]
        else:
            metadata: FFmpegMetadataPostprocessor = {"key": POSTPROCESSOR_METADATA}
            options["merge_output_format"] = VIDEO_CONTAINER
            options["postprocessors"] = [metadata]

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
    def _rename_entry_output(job_dir: Path, entry: dict, kind: MediaKind) -> DownloadedFile:
        video_id = entry.get("id")
        expected_ext = AUDIO_CODEC if kind == MediaKind.AUDIO else VIDEO_CONTAINER
        matches = list(job_dir.glob(f"{video_id}.{expected_ext}"))
        if not matches:
            raise DownloadError(f"Downloaded file not found for id {video_id}")

        original_file = matches[0]
        slug = slugify(entry.get("title", "media"))
        final_path = original_file.with_stem(f"{slug}-{video_id[:8]}")
        original_file.rename(final_path)

        # remove leftovers (ex: thumbnail image that wasn't cleaned up by yt-dlp)
        for leftover in job_dir.glob(f"{video_id}.*"):
            leftover.unlink(missing_ok=True)

        return DownloadedFile(
            file_name=final_path.name,
            file_path=str(final_path),
            file_size_bytes=final_path.stat().st_size,
        )
