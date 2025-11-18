from fastapi import APIRouter

from src.cifra_spotify.api.deps import SPOTIFY_AUTH
from src.cifra_spotify.app.schemas.auth_schema import LoginUrl

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/login", response_model=LoginUrl)
async def login(spotify_auth: SPOTIFY_AUTH) -> LoginUrl:
    url = spotify_auth.get_login_url()
    return LoginUrl(login_url=url)
