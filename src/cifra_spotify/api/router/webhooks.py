from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.cifra_spotify.api.deps import SPOTIFYDEPS
from src.cifra_spotify.app.core.logger import logger

router = APIRouter(prefix="/webhooks", tags=["WEBHOOKS"])


@router.get("/callback")
async def callback(code: Annotated[str, Query()], spotify: SPOTIFYDEPS):
    """
    Exchange the authorization code returned by Spotify for access and refresh tokens.

    This endpoint is called by Spotify after the user completes the login flow.
    It receives the ``code`` from the redirect URL and exchanges it for the tokens
    required to authenticate future Spotify API requests.
    """
    data = await spotify.auth.exchange_code_for_token(code)
    logger.info(f"Tokens obtidos: {data}")

    return {"status": "logado", "tokens": data}


class TrackInfo(BaseModel):
    id: str
    name: str
    artist: str
    progress_ms: int
    


@router.post("/spotify")
async def webhook(spotify: SPOTIFYDEPS, track: TrackInfo):
    logger.debug(f"Track changed: {track}")
    return {"status": "ok"}
