from typing import Literal, NotRequired, TypedDict

AudioCodec = Literal["mp3"]
AUDIO_CODEC: AudioCodec = "mp3"

POSTPROCESSOR_EXTRACT_AUDIO: Literal["FFmpegExtractAudio"] = "FFmpegExtractAudio"
POSTPROCESSOR_METADATA: Literal["FFmpegMetadata"] = "FFmpegMetadata"
POSTPROCESSOR_EMBED_THUMBNAIL: Literal["EmbedThumbnail"] = "EmbedThumbnail"

class FFmpegExtractAudioPostprocessor(TypedDict):
    key: Literal["FFmpegExtractAudio"]
    preferredcodec: AudioCodec

class FFmpegMetadataPostprocessor(TypedDict):
    key: Literal["FFmpegMetadata"]

class EmbedThumbnailPostprocessor(TypedDict):
    key: Literal["EmbedThumbnail"]

type YtDlpPostprocessorEntry = (
    FFmpegExtractAudioPostprocessor | FFmpegMetadataPostprocessor | EmbedThumbnailPostprocessor
)

class YtDlpOptions(TypedDict):
    outtmpl: str
    playlist_items: str
    format: str
    writethumbnail: NotRequired[bool]
    merge_output_format: NotRequired[str]
    postprocessors: NotRequired[list[YtDlpPostprocessorEntry]]
