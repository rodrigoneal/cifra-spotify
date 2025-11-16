from typing import List, Optional

from pydantic import BaseModel


class ExternalUrl(BaseModel):
    spotify: str


class Image(BaseModel):
    height: Optional[int]
    url: str
    width: Optional[int]


class Owner(BaseModel):
    display_name: Optional[str]
    external_urls: ExternalUrl
    href: str
    id: str
    type: str
    uri: str


class TracksInfo(BaseModel):
    href: str
    total: int


class PlaylistItem(BaseModel):
    collaborative: bool
    description: Optional[str]
    external_urls: ExternalUrl
    href: str
    id: str
    images: List[Image]
    name: str
    owner: Owner
    primary_color: Optional[str]
    public: Optional[bool]
    snapshot_id: str
    tracks: TracksInfo
    type: str
    uri: str


class Playlists(BaseModel):
    href: str
    limit: int
    next: Optional[str]
    offset: int
    previous: Optional[str]
    total: int
    items: List[PlaylistItem | None]  # <- agora suporta entradas nulas


class Playlist(BaseModel):
    collaborative: bool
    description: Optional[str]
    external_urls: ExternalUrl
    href: str
    id: str
    images: List[Image]
    name: str
    owner: Owner
    primary_color: Optional[str]
    public: Optional[bool]
    snapshot_id: str
    tracks: TracksInfo
    type: str
    uri: str


class SpotifySearchResponse(BaseModel):
    playlists: Playlists


class PlaylistsResponse(BaseModel):
    href: str
    items: List[Playlist]
