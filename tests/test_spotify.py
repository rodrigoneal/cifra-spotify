import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from cifra_spotify.spotify.spotify import SpotifyAPI
from cifra_spotify.spotify.auth import SpotifyAuth


@pytest.mark.asyncio
async def test_send_request():
    """_send_request deve enviar GET com token corretamente."""
    auth = MagicMock(spec=SpotifyAuth)
    auth.ensure_token = AsyncMock(return_value="TEST_TOKEN")

    api = SpotifyAPI(auth)

    mock_response = MagicMock(spec=httpx.Response)
    with patch.object(api.client, "get", new=AsyncMock(return_value=mock_response)) as mock_get:
        resp = await api._send_request("me", params={"x": "1"})

    assert resp is mock_response

    mock_get.assert_awaited_once_with(
        "https://api.spotify.com/v1/me",
        params={"x": "1"},
        headers={"Authorization": "Bearer TEST_TOKEN"},
    )


@pytest.mark.asyncio
async def test_me():
    """Deve chamar _send_request('me')."""
    auth = MagicMock(spec=SpotifyAuth)
    auth.ensure_token = AsyncMock(return_value="T")

    api = SpotifyAPI(auth)

    with patch.object(api, "_send_request", new=AsyncMock()) as mock_req:
        await api.me()
        mock_req.assert_awaited_once_with("me")


@pytest.mark.asyncio
async def test_get_current_track():
    """Deve chamar _send_request('me/player/currently-playing')."""
    auth = MagicMock(spec=SpotifyAuth)
    auth.ensure_token = AsyncMock(return_value="T")

    api = SpotifyAPI(auth)

    with patch.object(api, "_send_request", new=AsyncMock()) as mock_req:
        await api.get_current_track()
        mock_req.assert_awaited_once_with("me/player/currently-playing")


@pytest.mark.asyncio
async def test_search_track():
    """Deve fazer search de tracks com os parâmetros corretos."""
    auth = MagicMock(spec=SpotifyAuth)
    auth.ensure_token = AsyncMock(return_value="T")

    api = SpotifyAPI(auth)

    with patch.object(api, "_send_request", new=AsyncMock()) as mock_req:
        await api.search_track("samba", limit=5, offset=2)

        mock_req.assert_awaited_once_with(
            "search",
            params={"q": "samba", "type": "track", "limit": 5, "offset": 2},
        )


@pytest.mark.asyncio
async def test_get_my_playlists():
    """Deve retornar playlists paginadas."""
    auth = MagicMock(spec=SpotifyAuth)
    auth.ensure_token = AsyncMock(return_value="T")

    api = SpotifyAPI(auth)

    with patch.object(api, "_send_request", new=AsyncMock()) as mock_req:
        await api.get_my_playlists(limit=20, offset=40)

        mock_req.assert_awaited_once_with(
            "me/playlists",
            params={"limit": 20, "offset": 40},
        )


@pytest.mark.asyncio
async def test_search_playlist():
    """search_playlist deve chamar search com type=playlist."""
    auth = MagicMock(spec=SpotifyAuth)
    auth.ensure_token = AsyncMock(return_value="T")

    api = SpotifyAPI(auth)

    with patch.object(api, "_send_request", new=AsyncMock()) as mock_req:
        await api.search_playlist("pagode", limit=3, offset=1)

        mock_req.assert_awaited_once_with(
            "search",
            params={
                "q": "pagode",
                "type": "playlist",
                "limit": 3,
                "offset": 1,
            },
        )


@pytest.mark.asyncio
async def test_aclose():
    """aclose() deve fechar o client httpx."""
    auth = MagicMock(spec=SpotifyAuth)
    auth.ensure_token = AsyncMock(return_value="T")

    api = SpotifyAPI(auth)

    with patch.object(api.client, "aclose", new=AsyncMock()) as mock_close:
        await api.aclose()
        mock_close.assert_awaited_once()
