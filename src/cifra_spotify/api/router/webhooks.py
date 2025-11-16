from typing import Annotated

from fastapi import APIRouter, Query

from src.cifra_spotify.api.deps import SPOTIFYDEPS

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

    return {"status": "logado", "tokens": data}
