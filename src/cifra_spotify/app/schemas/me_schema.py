from pydantic import BaseModel


class ExternalUrl(BaseModel):
    spotify: str


class Followers(BaseModel):
    href: str | None
    total: int


class Image(BaseModel):
    height: int | None
    url: str
    width: int | None


class SpotifyUser(BaseModel):
    display_name: str | None
    external_urls: ExternalUrl
    followers: Followers
    href: str
    id: str
    images: list[Image]
    type: str
    uri: str
