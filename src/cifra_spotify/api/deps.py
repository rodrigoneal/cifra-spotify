from typing import Annotated, TypeAlias

import httpx
from fastapi import Depends, Request

from cifra_spotify.cifras.cifra_club.cifra_club import CifraClub
from cifra_spotify.cifras.cifra_club.infrastructure.http.http_client import (
    CifraClubHttpClient,
)
from cifra_spotify.spotify import clients as spotify_clients
from src.cifra_spotify.spotify.services.spotify_service import SpotifyService


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.client


def get_spotify_auth(request: Request) -> spotify_clients.SpotifyAuth:
    return request.app.state.spotify_auth


def get_spotify_api() -> spotify_clients.SpotifyAPI:
    return spotify_clients.SpotifyAPI()


def get_spotify_client(
    auth: spotify_clients.SpotifyAuth = Depends(get_spotify_auth),
    client: httpx.AsyncClient = Depends(get_http_client),
) -> spotify_clients.SpotifyClient:
    return spotify_clients.SpotifyClient(auth=auth, client=client)


def get_spotify_service(
    client: spotify_clients.SpotifyClient = Depends(get_spotify_client),
) -> SpotifyService:
    return SpotifyService(client=client)


def get_spotify_facade(
    service: SpotifyService = Depends(get_spotify_service),
) -> spotify_clients.Spotify:
    return spotify_clients.Spotify(service=service)


def get_cifra_club_http_client(
    client: httpx.AsyncClient = Depends(get_http_client),
) -> CifraClubHttpClient:
    return CifraClubHttpClient(client=client)


def get_cifra_club(
    client: CifraClubHttpClient = Depends(get_cifra_club_http_client),
) -> CifraClub:
    return CifraClub(client=client)


CIFRACLUB: TypeAlias = Annotated[CifraClub, Depends(get_cifra_club)]
SPOTIFY_CLIENT = Annotated[spotify_clients.SpotifyClient, Depends(get_spotify_client)]

SPOTIFY_AUTH = Annotated[spotify_clients.SpotifyAuth, Depends(get_spotify_auth)]
SPOTIFY_FACADE = Annotated[spotify_clients.Spotify, Depends(get_spotify_facade)]
