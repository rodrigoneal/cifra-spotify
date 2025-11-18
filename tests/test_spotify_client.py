from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest
from tenacity import RetryError

from src.cifra_spotify.app.custom_exceptions.exceptions import AuthRetry
from src.cifra_spotify.app.schemas.track_schema import SpotifyCurrentlyPlaying
from src.cifra_spotify.spotify.clients.spotify_client import SpotifyClient


@pytest.fixture
def mock_auth():
    auth = MagicMock()
    auth.ensure_token = AsyncMock(return_value="TOKEN123")
    auth.refresh_access_token = AsyncMock()
    return auth


@pytest.fixture
def mock_http():
    client = MagicMock(spec=httpx.AsyncClient)
    client.get = AsyncMock()
    return client


@pytest.fixture
def spotify_client(mock_auth, mock_http):
    return SpotifyClient(auth=mock_auth, client=mock_http)


def make_response(status_code, json_data=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json = lambda: json_data
    return resp


@pytest.mark.asyncio
async def test_request_ok(spotify_client, mock_http):
    mock_http.get.return_value = make_response(200, {"ok": True})

    data = await spotify_client._request("http://test")

    assert data == {"ok": True}


@pytest.mark.asyncio
async def test_request_no_content(spotify_client, mock_http):
    mock_http.get.return_value = make_response(204)

    data = await spotify_client._request("http://test")

    assert data is None


@pytest.mark.asyncio
async def test_request_unauthorized(spotify_client, mock_http, mock_auth):
    mock_http.get.return_value = make_response(401)

    with pytest.raises(AuthRetry):
        await spotify_client._request("http://test")

    mock_auth.refresh_access_token.assert_called_once()


@pytest.mark.asyncio
async def test_request_http_error(spotify_client, mock_http):
    mock_http.get.return_value = make_response(500)

    with pytest.raises(AuthRetry):
        await spotify_client._request("http://test")


@pytest.mark.asyncio
async def test_request_network_error(spotify_client, mock_http):
    mock_http.get.side_effect = httpx.RequestError("network error")

    with pytest.raises(AuthRetry):
        await spotify_client._request("http://test")


@pytest.mark.asyncio
async def test_get_me_success(spotify_client, mock_http):
    mock_http.get.return_value = make_response(
        200,
        {
            "display_name": "Rodrigo",
            "external_urls": {"spotify": "https://open.spotify.com/user/123"},
            "followers": {"href": None, "total": 10},
            "href": "https://api.spotify.com/v1/users/123",
            "id": "123",
            "images": [],
            "type": "user",
            "uri": "spotify:user:123",
        },
    )

    result = await spotify_client.get_me()

    assert result.id == "123"
    assert result.display_name == "Rodrigo"


@pytest.mark.asyncio
async def test_get_currently_playing_success(spotify_client, mock_http):
    mock_http.get.return_value = make_response(
        200,
        {
            "device": {
                "id": "string",
                "is_active": False,
                "is_private_session": False,
                "is_restricted": False,
                "name": "Kitchen speaker",
                "type": "computer",
                "volume_percent": 59,
                "supports_volume": False,
            },
            "repeat_state": "off",
            "shuffle_state": False,
            "context": {
                "type": "artist",
                "href": "string",
                "external_urls": {"spotify": "string"},
                "uri": "string",
            },
            "timestamp": 0,
            "progress_ms": 0,
            "is_playing": True,
            "item": {
                "album": {
                    "album_type": "compilation",
                    "total_tracks": 9,
                    "available_markets": ["BR"],
                    "external_urls": {"spotify": "string"},
                    "href": "string",
                    "id": "alb1",
                    "images": [{"url": "http://img.com", "height": 300, "width": 300}],
                    "name": "Album Teste",
                    "release_date": "1981-12",
                    "release_date_precision": "year",
                    "type": "album",
                    "uri": "spotify:album:1",
                    "artists": [
                        {
                            "external_urls": {"spotify": "string"},
                            "href": "string",
                            "id": "art1",
                            "name": "Rodrigo",
                            "type": "artist",
                            "uri": "spotify:artist:1",
                        }
                    ],
                },
                "artists": [
                    {
                        "external_urls": {"spotify": "string"},
                        "href": "string",
                        "id": "art1",
                        "name": "Rodrigo",
                        "type": "artist",
                        "uri": "spotify:artist:1",
                    }
                ],
                "available_markets": ["BR"],
                "disc_number": 1,
                "duration_ms": 200000,
                "explicit": False,
                "external_ids": {"isrc": "ABC", "ean": "123", "upc": "456"},
                "external_urls": {"spotify": "string"},
                "href": "string",
                "id": "track123",
                "is_playable": True,
                "name": "Minha Música",
                "popularity": 80,
                "preview_url": None,
                "track_number": 1,
                "type": "track",
                "uri": "spotify:track:1",
                "is_local": False,
            },
            "currently_playing_type": "track",
            "actions": {
                "interrupting_playback": False,
                "pausing": False,
                "resuming": False,
                "seeking": False,
                "skipping_next": False,
                "skipping_prev": False,
                "toggling_repeat_context": False,
                "toggling_shuffle": False,
                "toggling_repeat_track": False,
                "transferring_playback": False,
            },
        },
    )

    result = await spotify_client.get_currently_playing()

    assert isinstance(result, SpotifyCurrentlyPlaying)
    assert result.is_playing is True
    assert result.item.name == "Minha Música"
    assert result.device.name == "Kitchen speaker"
    assert result.item.album.images[0].url == "http://img.com"


@pytest.mark.asyncio
async def test_search_track_success(spotify_client, mock_http):
    mock_http.get.return_value = make_response(
        200,
        {
            "device": {
                "id": "string",
                "is_active": False,
                "is_private_session": False,
                "is_restricted": False,
                "name": "Kitchen speaker",
                "type": "computer",
                "volume_percent": 59,
                "supports_volume": False,
            },
            "repeat_state": "off",
            "shuffle_state": False,
            "context": {
                "type": "artist",
                "href": "string",
                "external_urls": {"spotify": "string"},
                "uri": "string",
            },
            "timestamp": 0,
            "progress_ms": 0,
            "is_playing": True,
            "item": {
                "album": {
                    "album_type": "compilation",
                    "total_tracks": 9,
                    "available_markets": ["BR"],
                    "external_urls": {"spotify": "string"},
                    "href": "string",
                    "id": "alb1",
                    "images": [{"url": "http://img.com", "height": 300, "width": 300}],
                    "name": "Album Teste",
                    "release_date": "1981-12",
                    "release_date_precision": "year",
                    "type": "album",
                    "uri": "spotify:album:1",
                    "artists": [
                        {
                            "external_urls": {"spotify": "string"},
                            "href": "string",
                            "id": "art1",
                            "name": "Rodrigo",
                            "type": "artist",
                            "uri": "spotify:artist:1",
                        }
                    ],
                },
                "artists": [
                    {
                        "external_urls": {"spotify": "string"},
                        "href": "string",
                        "id": "art1",
                        "name": "Rodrigo",
                        "type": "artist",
                        "uri": "spotify:artist:1",
                    }
                ],
                "available_markets": ["BR"],
                "disc_number": 1,
                "duration_ms": 200000,
                "explicit": False,
                "external_ids": {"isrc": "ABC", "ean": "123", "upc": "456"},
                "external_urls": {"spotify": "string"},
                "href": "string",
                "id": "track123",
                "is_playable": True,
                "name": "Minha Música",
                "popularity": 80,
                "preview_url": None,
                "track_number": 1,
                "type": "track",
                "uri": "spotify:track:1",
                "is_local": False,
            },
            "currently_playing_type": "track",
            "actions": {
                "interrupting_playback": False,
                "pausing": False,
                "resuming": False,
                "seeking": False,
                "skipping_next": False,
                "skipping_prev": False,
                "toggling_repeat_context": False,
                "toggling_shuffle": False,
                "toggling_repeat_track": False,
                "transferring_playback": False,
            },
        },
    )

    result = await spotify_client.search_track("test")

    assert result.item.track_number == 1


@pytest.mark.asyncio
async def test_get_my_playlists_success(spotify_client, mock_http):
    mock_http.get.return_value = make_response(200, {"items": [{"name": "A"}]})

    result = await spotify_client.get_my_playlists()

    assert result.items[0].name == "A"


@pytest.mark.asyncio
async def test_search_playlist_success(spotify_client, mock_http):
    mock_http.get.return_value = make_response(
        200, {"playlists": {"items": [{"name": "Playlist"}]}}
    )

    result = await spotify_client.search_playlist("abc")

    assert result.playlists.items[0].name == "Playlist"


@pytest.mark.asyncio
async def test_retry_is_triggered(spotify_client, mock_http):
    """
    O método deve tentar 3 vezes e depois disparar RetryError.
    """

    mock_http.get.return_value = make_response(500)

    with pytest.raises(RetryError):
        await spotify_client.get_me()  # decorado com retry

    assert mock_http.get.call_count == 3  # é o padrão stop_after_attempt(3)
