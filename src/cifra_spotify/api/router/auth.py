from fastapi import APIRouter

from src.cifra_spotify.api.deps import SPOTIFYDEPS

router = APIRouter(prefix="/api/auth", tags=["AUTH"])


@router.get("/login")
async def login(spotify: SPOTIFYDEPS):
    """
    Generate the Spotify authentication URL.

    This endpoint returns the URL that the user must visit to authenticate with Spotify.
    After logging in, Spotify will redirect the user to the configured `redirect_uri`
    along with an authorization code used to obtain access tokens.
    """
    return {"url_login": spotify.auth.get_login_url(), "status": "ok"}
