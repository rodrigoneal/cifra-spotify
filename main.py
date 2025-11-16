import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cifra_spotify.spotify.pooling import SpotifyPollingService
from src.cifra_spotify.api import register_routers
from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.custom_exceptions import register_exception_handlers

try:
    import uvloop
except ImportError:
    uvloop = None

if uvloop and sys.platform != "win32":
    logger.info("Using uvloop")
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")
    from src.cifra_spotify.api.deps import spotify

    app.state.poller = SpotifyPollingService(spotify)
    await app.state.poller.start()
    yield
    await spotify.aclose()
    await app.state.poller.stop()
    logger.info("Application stopped.")


def create_app():
    """
    Create and configure the FastAPI application instance.

    This function initializes the main FastAPI app, registers all API routers
    (Spotify authentication, playlists, tracks, etc.), and sets up the custom
    exception handlers used throughout the application.

    Returns:
        FastAPI: A fully configured FastAPI application ready to run.
    """
    app = FastAPI(
        title="Cifra Spotify API",
        summary="Spotify integration API for reading music data and generating chord sheets.",
        description=(
            "This API performs OAuth authentication with Spotify, retrieves user "
            "profile information, fetches the currently playing track, searches for "
            "songs and playlists, and provides the foundation for generating "
            "automatic chord sheets based on Spotify track metadata."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    # Register API routers
    register_routers(app)

    # Register custom exception handlers
    register_exception_handlers(app)

    return app


app = create_app()
