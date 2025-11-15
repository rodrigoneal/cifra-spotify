from fastapi import APIRouter

from src.cifra_spotify.api.deps import SPOTIFYDEPS

router = APIRouter(prefix="/api", tags=["ME"])


@router.get("/")
async def me(spotify: SPOTIFYDEPS = None):
    return await spotify.me()
