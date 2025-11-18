from src.cifra_spotify.app.schemas.service_schema import CurrentlyPlaying
from src.cifra_spotify.spotify.services.spotify_service import SpotifyService


class Spotify:
    def __init__(self, service: SpotifyService):
        self.spotify_service = service

    async def get_currently_playing(self) -> CurrentlyPlaying:
        return await self.spotify_service.get_currently_playing()
