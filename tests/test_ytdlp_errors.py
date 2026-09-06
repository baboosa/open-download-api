from open_download_api.core.ytdlp_errors import is_retryable_error


def test_incomplete_id_is_not_retryable():
    assert is_retryable_error("Incomplete YouTube ID abc123.") is False

def test_bot_detection_is_not_retryable():
    message = "Sign in to confirm you're not a bot. Use --cookies..."
    assert is_retryable_error(message) is False

def test_generic_network_error_is_retryable():
    assert is_retryable_error("HTTP Error 503: Service Unavailable") is True
