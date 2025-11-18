from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True)
class SpotifyAPI:
    BASE_URL: str = "https://api.spotify.com/v1"

    @staticmethod
    def currently_playing() -> str:
        return f"{SpotifyAPI.BASE_URL}/me/player/currently-playing"

    @staticmethod
    def me() -> str:
        return f"{SpotifyAPI.BASE_URL}/me"

    @staticmethod
    def search() -> str:
        return f"{SpotifyAPI.BASE_URL}/search"

    @staticmethod
    def my_playlists() -> str:
        return f"{SpotifyAPI.BASE_URL}/me/playlists"
