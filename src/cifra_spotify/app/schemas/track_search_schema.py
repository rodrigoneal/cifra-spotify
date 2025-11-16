from pydantic import BaseModel
from typing import Any


class ExternalUrl(BaseModel):
    spotify: str


class Image(BaseModel):
    height: int | None
    url: str
    width: int | None


class Artist(BaseModel):
    external_urls: ExternalUrl
    href: str
    id: str
    name: str
    type: str
    uri: str


class Album(BaseModel):
    album_type: str
    total_tracks: int
    available_markets: list[str]
    external_urls: ExternalUrl
    href: str
    id: str
    images: list[Image]
    name: str
    release_date: str
    release_date_precision: str
    type: str
    uri: str
    artists: list[Artist]


class ExternalId(BaseModel):
    isrc: str | None


class Track(BaseModel):
    album: Album
    artists: list[Artist]
    available_markets: list[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: ExternalId
    external_urls: ExternalUrl
    href: str
    id: str
    is_local: bool
    is_playable: bool | None
    name: str
    popularity: int
    preview_url: str | None
    track_number: int
    type: str
    uri: str


class Tracks(BaseModel):
    href: str
    limit: int
    next: str | None
    offset: int
    previous: str | None
    total: int
    items: list[Track]


class SpotifyTrackSearchResponse(BaseModel):
    tracks: Tracks
