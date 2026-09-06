PERMANENT_ERROR_MARKERS = (
    "Incomplete YouTube ID",
    "Video unavailable",
    "Private video",
    "This video is unavailable",
    "Sign in to confirm you're not a bot",
)


def is_retryable_error(error_message: str) -> bool:
    return not any(marker in error_message for marker in PERMANENT_ERROR_MARKERS)
