from fastapi import APIRouter

from src.cifra_spotify.api.deps import SPOTIFYDEPS

router = APIRouter(prefix="/api/auth", tags=["AUTH"])


@router.get("/login")
async def login(spotify: SPOTIFYDEPS):
    return {"url_login": spotify.auth.get_login_url(), "status": "ok"}
