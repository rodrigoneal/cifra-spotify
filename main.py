import asyncio
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI

from cifra_spotify.api import register_routers
from cifra_spotify.app.core.logger import logger
from cifra_spotify.app.custom_exceptions import register_exception_handlers

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
    yield
    logger.info("Stopping application...")

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
        description="""
                ## Overview

                The **Cifra Spotify API** integrates with the Spotify Web API to retrieve music data
                and support automatic chord sheet generation for songs.

                This service authenticates users via **Spotify OAuth 2.0** and provides endpoints
                to access Spotify user information, currently playing tracks, and search results
                for songs and playlists.

                The API is designed to serve as the backend foundation for applications focused on
                **music analysis, chord generation, and musician tools**.

                ---

                ## Features

                ### Spotify Authentication
                Secure user authentication using **Spotify OAuth 2.0**.

                ### User Profile
                Retrieve Spotify user profile information such as:
                - Display name
                - User ID
                - Account details

                ### Currently Playing Track
                Fetch information about the track currently playing on the user's Spotify account.

                ### Music Search
                Search Spotify for:
                - Tracks
                - Artists
                - Albums
                - Playlists

                ### Chord Sheet Generation
                Use Spotify track metadata to support the generation of **automatic chord sheets**
                for musicians.

                ---

                ## Typical Use Case

                1. Authenticate the user with Spotify
                2. Retrieve user profile data
                3. Fetch the currently playing track
                4. Use track metadata to search for chords
                5. Generate chord sheets for the song

                ---

                ## Target Applications

                - Music practice tools
                - Automatic chord generators
                - Jam session assistants
                - Music learning platforms
                """,
        version="1.0.0",
        lifespan=lifespan,
    )

    # Register API routers
    register_routers(app)

    # Register custom exception handlers
    register_exception_handlers(app)

    return app


app = create_app()
