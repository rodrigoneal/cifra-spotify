from dataclasses import dataclass

from src.cifra_spotify.app.custom_exceptions.exceptions import NotPlayeringException
from src.cifra_spotify.cifras.util import normalize_track_title
from src.cifra_spotify.spotify.spotify import SpotifyAPI


@dataclass
class SongData:
    track_name: str
    artist_name: str
    artist_id: str
    genres: list[str]


def parser_spotify(track: dict) -> SongData:
    breakpoint()
    parcial_track = track["item"]
    data = {
        "music_name": normalize_track_title(parcial_track["name"]),
        "artist": parcial_track["artists"][0]["name"],
    }
    return SongData(**data)


async def get_current_track_with_genres(spotify: SpotifyAPI) -> SongData | None:
    current = await spotify.get_current_track()

    if current.status_code == 204:
        raise NotPlayeringException(
            message="No track is currently playing", status_code=404
        )

    data = current.json()
    item = data.get("item")
    if not item:
        return None

    artists = item.get("artists") or []
    first_artist = artists[0] if artists else None

    genres = []
    if first_artist and first_artist.get("id"):
        artist_response = await spotify.get_artist(first_artist["id"])
        artist_data = artist_response.json()
        genres = artist_data.get("genres", [])

    result = {
        "track_name": item.get("name"),
        "artist_name": first_artist.get("name") if first_artist else None,
        "artist_id": first_artist.get("id") if first_artist else None,
        "genres": genres,
    }

    return SongData(**result)
