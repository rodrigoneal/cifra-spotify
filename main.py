import asyncio
import sys
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from src.cifra_spotify.api.routers import register_routers
from src.cifra_spotify.app.core.config import settings
from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.custom_exceptions import register_exception_handlers
from src.cifra_spotify.spotify.clients.spotify_auth import SpotifyAuth
from src.cifra_spotify.spotify.clients.spotify_token_storage import SpotifyTokenStorage

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
    http_client = httpx.AsyncClient(timeout=10, follow_redirects=True)
    spotify_token_storage = SpotifyTokenStorage(
        filepath=settings.SPOTIFY_TOKEN_FILE, key=settings.TOKEN_KEY
    )
    spotify_auth = SpotifyAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        client=http_client,
        storage=spotify_token_storage,
    )
    await spotify_auth.init()
    app.state.client = http_client
    app.state.spotify_auth = spotify_auth
    try:
        yield
    finally:
        await app.state.client.aclose()


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
        summary="API de integração com o Spotify para leitura de dados musicais e gerenciamento de autenticação OAuth.",
        description=(
            """Esta API executa autenticação OAuth com o Spotify, obtém informações básicas do usuário autenticado,
            acessa a faixa atualmente em reprodução e permite consultar músicas e playlists. Ela também fornece endpoints
            internos que servirão como base para futuros módulos de geração de cifras e processamento de metadados musicais."""
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
