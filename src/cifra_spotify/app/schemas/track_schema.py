from typing import List, Literal, Optional

from pydantic import BaseModel


class ExternalUrls(BaseModel):
    spotify: str


class Image(BaseModel):
    height: int
    url: str
    width: int


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
    isrc: Optional[str] = None


class TrackItem(BaseModel):
    album: Album
    artists: List[Artist]
    available_markets: List[str]
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
    preview_url: Optional[str]
    track_number: int
    type: str
    uri: str


class Context(BaseModel):
    external_urls: ExternalUrls
    href: str
    type: str
    uri: str


class Disallows(BaseModel):
    pausing: Optional[bool] = None
    skipping_prev: Optional[bool] = None


class Actions(BaseModel):
    disallows: Disallows


class SpotifyCurrentlyPlaying(BaseModel):
    is_playing: bool
    timestamp: int
    context: Optional[Context] = None
    progress_ms: Optional[int] = None
    item: Optional[TrackItem] = None
    currently_playing_type: str
    actions: Optional[Actions] = None


class CurrentTrackNotFound(BaseModel):
    is_playing: Literal[False] = False
    currently_playing_type: Literal["track"] = "track"
