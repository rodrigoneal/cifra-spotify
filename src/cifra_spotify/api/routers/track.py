from fastapi import APIRouter

from src.cifra_spotify.api.deps import SPOTIFY_FACADE
from src.cifra_spotify.app.schemas.service_schema import CurrentlyPlaying

router = APIRouter(prefix="/track", tags=["track"])


@router.get("/currrent_playing", response_model=CurrentlyPlaying)
async def get_current_track(spotify: SPOTIFY_FACADE) -> None:
    return await spotify.get_currently_playing()
