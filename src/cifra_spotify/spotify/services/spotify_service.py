from __future__ import annotations

from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.schemas.service_schema import CurrentlyPlaying

# from src.cifra_spotify.spotify.clients.spotify_client import SpotifyClient


class SpotifyService:
    def __init__(self, client: "SpotifyClient"):
        self.client = client

    async def get_currently_playing(self) -> CurrentlyPlaying:
        try:
            data = await self.client.get_currently_playing()
            if not data or not data.item:
                raise Exception("No track playing")
            track = data.item
            result = {
                "track_id": track.id,
                "track_name": track.name,
                "artist_name": track.artists[0].name if track.artists else None,
                "progress_ms": data.progress_ms,
                "is_playing": data.is_playing,
            }
        except Exception as e:
            logger.error(e)
            result = {
                "track_id": None,
                "track_name": None,
                "artist_name": None,
                "progress_ms": None,
                "is_playing": False,
            }

        return CurrentlyPlaying.model_validate(result)
