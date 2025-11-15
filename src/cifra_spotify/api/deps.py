from typing import Annotated

from fastapi import Depends

from src.cifra_spotify.spotify import SpotifyAPI, spotify


def get_spotify() -> SpotifyAPI:
    return spotify


SPOTIFYDEPS = Annotated[SpotifyAPI, Depends(get_spotify)]
