from typing import List, Literal

from pydantic import BaseModel


class ExternalUrls(BaseModel):
    spotify: str


class Image(BaseModel):
    height: int
    url: str
    width: int
    

class Device(BaseModel):
    id: str
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: str
    volume_percent: int
    supports_volume: bool


class Artist(BaseModel):
    external_urls: ExternalUrls
    href: str
    id: str
    name: str
    type: str
    uri: str


class Album(BaseModel):
    album_type: str
    artists: List[Artist]
    available_markets: List[str]
    external_urls: ExternalUrls
    href: str
    id: str
    images: List[Image]
    name: str
    release_date: str
    release_date_precision: str
    total_tracks: int
    type: str
    uri: str


class ExternalIds(BaseModel):
    isrc: str|None = None


class TrackItem(BaseModel):
    album: Album
    artists: list[Artist]
    available_markets: list[str]
    disc_number: int
    duration_ms: int
    explicit: bool
    external_ids: ExternalIds
    external_urls: ExternalUrls
    href: str
    id: str
    is_local: bool
    name: str
    popularity: int
    preview_url: str | None = None
    track_number: int
    type: str
    uri: str


class Context(BaseModel):
    external_urls: ExternalUrls
    href: str
    type: str
    uri: str


class Disallows(BaseModel):
    pausing: bool | None = None
    skipping_prev: bool | None = None


class Actions(BaseModel):
    pausing: bool | None = None
    skipping_prev: bool | None = None


class SpotifyCurrentlyPlaying(BaseModel):
    is_playing: bool = False
    timestamp: int = 0
    context: Context | None = None
    progress_ms: int | None = None
    item: TrackItem | None = None
    currently_playing_type: str = "track"
    actions: Actions | None = None
    device: Device | None = None


# class CurrentTrackNotFound(BaseModel):
#     is_playing: Literal[False] = False
#     currently_playing_type: Literal["track"] = "track"
