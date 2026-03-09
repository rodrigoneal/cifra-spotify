import asyncio
import signal

from src.cifra_spotify.api.deps import spotify
from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.spotify.pooling import SpotifyPollingService


async def main():
    stop_event = asyncio.Event()

    service = SpotifyPollingService(api=spotify)

    def _handle_stop(*_):
        logger.info("Shutdown signal received.")
        stop_event.set()

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _handle_stop)
        except NotImplementedError:
            pass

    await service.start()
    logger.info("Spotify polling worker started.")

    try:
        await stop_event.wait()
    finally:
        await service.stop()
        await spotify.aclose()
        logger.info("Spotify polling worker stopped.")


if __name__ == "__main__":
    asyncio.run(main())
    logger.info("Spotify polling worker stopped.")
