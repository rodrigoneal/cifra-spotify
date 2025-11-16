import os
import time
import pytest
from unittest.mock import patch, mock_open, AsyncMock
import httpx

from src.cifra_spotify.spotify.auth import SpotifyAuth


@pytest.fixture
def spotify_auth():
    return SpotifyAuth("client_id", "client_secret", "http://localhost/callback")


def test_get_login_url(spotify_auth):
    url = spotify_auth.get_login_url()
    assert url.startswith("https://accounts.spotify.com/authorize?")
    assert "client_id=client_id" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%2Fcallback" in url
    assert "response_type=code" in url


@patch("builtins.open", new_callable=mock_open, read_data="access\nrefresh\n123456")
@patch("os.path.exists", return_value=True)
def test_load_from_file(mock_exists, mock_file):
    auth = SpotifyAuth("id", "secret", "uri")
    assert auth.access_token == "access"
    assert auth.refresh_token == "refresh"
    assert auth.expires_at == 123456


@patch("builtins.open", new_callable=mock_open)
def test_save_to_file(mock_file, spotify_auth):
    spotify_auth.access_token = "a"
    spotify_auth.refresh_token = "r"
    spotify_auth.expires_at = 42

    spotify_auth._save_to_file()
    mock_file().write.assert_called_once_with("a\nr\n42")


@pytest.mark.asyncio
async def test_exchange_code_for_token(spotify_auth):
    # Criar mock do response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json =  AsyncMock(return_value={
        "access_token": "new_access",
        "refresh_token": "new_refresh",
        "expires_in": 3600,
    })
    

    with patch("httpx.AsyncClient.post", return_value=mock_response) as mock_post, \
         patch.object(spotify_auth, "_save_to_file") as mock_save:

        data = await spotify_auth.exchange_code_for_token("code123")
        breakpoint()

        assert spotify_auth.access_token == "new_access"
        assert spotify_auth.refresh_token == "new_refresh"
        assert spotify_auth.expires_at > 0
        assert data["access_token"] == "new_access"
        mock_save.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.post", new_callable=AsyncMock)
@patch.object(SpotifyAuth, "_save_to_file")
async def test_refresh_access_token(mock_save, mock_post, spotify_auth):
    spotify_auth.refresh_token = "rtoken"
    mock_post.return_value.json.return_value = {"access_token": "access2", "expires_in": 3600}
    mock_post.return_value.status_code = 200

    data = await spotify_auth.refresh_access_token()

    assert spotify_auth.access_token == "access2"
    assert data["access_token"] == "access2"
    mock_save.assert_called_once()


@pytest.mark.asyncio
@patch.object(SpotifyAuth, "refresh_access_token", new_callable=AsyncMock)
async def test_ensure_token_refresh(mock_refresh, spotify_auth):
    spotify_auth.access_token = "a"
    spotify_auth.expires_at = time.time() - 10  # expirado

    await spotify_auth.ensure_token()
    mock_refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_ensure_token_no_access_raises(spotify_auth):
    spotify_auth.access_token = None
    with pytest.raises(Exception, match="User not authenticated"):
        await spotify_auth.ensure_token()
