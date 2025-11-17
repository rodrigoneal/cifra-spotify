from pydantic import BaseModel
from src.cifra_spotify.spotify.clients.spotify_client import SpotifyClient


class CurrentlyPlaying(BaseModel):
    track_id: str
    track_name: str
    artist_name: str
    progress_ms: int


class SpotifyService:
    def __init__(self, client: SpotifyClient):
        self.client = client

    async def get_currently_playing(self) -> CurrentlyPlaying:
        data = await self.client.get_currently_playing()

        if not data or not data.item:
            return None  # nada tocando agora

        track = data.item
        pre_data = {
            "track_id": track.id,
            "track_name": track.name,
            "artist_name": track.artists[0].name if track.artists else None,
            "progress_ms": data.progress_ms,
        }

        return CurrentlyPlaying.model_validate(pre_data)
