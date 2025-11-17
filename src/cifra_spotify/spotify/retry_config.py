import logging
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    before_sleep_log,
)
from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.spotify.clients.spotify_client import AuthRetry


def spotify_retry():
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(AuthRetry),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
