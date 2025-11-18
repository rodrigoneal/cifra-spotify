from typing import Annotated

import httpx
from fastapi import Depends, Request

from src.cifra_spotify.spotify import clients
from src.cifra_spotify.spotify.clients.spotify import Spotify
from src.cifra_spotify.spotify.services.spotify_service import SpotifyService


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.client


def get_spotify_auth(request: Request) -> clients.SpotifyAuth:
    return request.app.state.spotify_auth


def get_spotify_api() -> clients.SpotifyAPI:
    return clients.SpotifyAPI()


def get_spotify_client(
    auth: clients.SpotifyAuth = Depends(get_spotify_auth),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> clients.SpotifyClient:
    return clients.SpotifyClient(auth=auth, client=client)


def get_spotify_service(
    client: clients.SpotifyClient = Depends(get_spotify_client),
) -> SpotifyService:
    return SpotifyService(client=client)


def get_spotify_facade(
    service: SpotifyService = Depends(get_spotify_service),
) -> Spotify:
    return clients.Spotify(service=service)


SPOTIFY_AUTH = Annotated[clients.SpotifyAuth, Depends(get_spotify_auth)]
SPOTIFY_FACADE = Annotated[Spotify, Depends(get_spotify_facade)]
