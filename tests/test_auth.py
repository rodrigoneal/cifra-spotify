# tests/test_spotify_auth.py
import json
import time
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from src.cifra_spotify.app.custom_exceptions.exceptions import (
    SpotifyAuthException,
    UserNotAuthenticatedException,
)
from src.cifra_spotify.app.schemas.token import TokenData
from src.cifra_spotify.spotify.clients.spotify_auth import SpotifyAuth


@pytest.fixture
def mock_client():
    client = AsyncMock(spec=httpx.AsyncClient)
    return client


@pytest.fixture
def spotify_auth(tmp_path, mock_client):
    # sobrescrevendo o TOKEN_FILE para não mexer na home
    auth = SpotifyAuth(
        client=mock_client,
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost/callback",
    )
    auth.TOKEN_FILE = tmp_path / "token.enc"
    return auth


@pytest.mark.asyncio
async def test_get_login_url(spotify_auth):
    url = spotify_auth.get_login_url()
    assert "client_id=test_client_id" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%2Fcallback" in url
    assert "response_type=code" in url


@pytest.mark.asyncio
async def test_save_and_load_file(spotify_auth):
    # set token manually
    spotify_auth._access_token = "access123"
    spotify_auth.refresh_token = "refresh123"
    spotify_auth.expires_in = 123456.0

    await spotify_auth._save_to_file()
    loaded = await spotify_auth._load_from_file()
    assert loaded.access_token == "access123"
    assert loaded.refresh_token == "refresh123"
    assert loaded.expires_in == 123456.0


@pytest.mark.asyncio
async def test_delete_file(spotify_auth):
    # criar arquivo dummy
    await spotify_auth._save_to_file()
    assert spotify_auth.TOKEN_FILE.exists()
    await spotify_auth._delete_file()
    assert not spotify_auth.TOKEN_FILE.exists()


@pytest.mark.asyncio
async def test_exchange_code_for_token_success(spotify_auth, mock_client):
    fake_response = {
        "access_token": "access456",
        "refresh_token": "refresh456",
        "expires_in": 4600,
    }

    mock_post = AsyncMock()
    mock_post.status_code = 200
    mock_post.aread = AsyncMock(return_value=json.dumps(fake_response).encode())
    mock_client.post.return_value = mock_post

    fixed_time = 1000
    with patch("time.time", return_value=fixed_time):
        token = await spotify_auth.exchange_code_for_token("fake_code")

    assert isinstance(token, TokenData)
    assert token.access_token == "access456"
    assert token.refresh_token == "refresh456"
    # Agora token.expires_in é determinístico
    assert token.expires_in == fixed_time + 3600


@pytest.mark.asyncio
async def test_exchange_code_for_token_fail(spotify_auth, mock_client):
    mock_client.post.return_value.status_code = 400
    mock_client.post.return_value.aread = AsyncMock(return_value=b"{}")

    with pytest.raises(SpotifyAuthException):
        await spotify_auth.exchange_code_for_token("bad_code")


@pytest.mark.asyncio
async def test_refresh_access_token_success(spotify_auth, mock_client):
    spotify_auth.refresh_token = "refresh456"
    fake_response = {
        "access_token": "new_access",
        "refresh_token": "new_refresh",
        "expires_in": 3600,
    }
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.aread = AsyncMock(
        return_value=json.dumps(fake_response).encode()
    )

    token = await spotify_auth.refresh_access_token()
    assert token.access_token == "new_access"
    assert token.refresh_token == "new_refresh"


@pytest.mark.asyncio
async def test_refresh_access_token_fail(spotify_auth, mock_client):
    spotify_auth.refresh_token = "refresh456"
    mock_client.post.return_value.status_code = 400
    mock_client.post.return_value.text = "fail"
    mock_client.post.return_value.aread = AsyncMock(return_value=b"{}")

    with pytest.raises(SpotifyAuthException):
        await spotify_auth.refresh_access_token()


@pytest.mark.asyncio
async def test_ensure_token_refresh_if_expired(spotify_auth, mock_client):
    # token expirado
    spotify_auth._access_token = "old"
    spotify_auth.refresh_token = "refresh"
    spotify_auth.expires_in = time.time() - 10

    fake_response = {
        "access_token": "new_access",
        "refresh_token": "new_refresh",
        "expires_in": 3600,
    }
    mock_client.post.return_value.status_code = 200
    mock_client.post.return_value.aread = AsyncMock(
        return_value=json.dumps(fake_response).encode()
    )

    token = await spotify_auth.ensure_token()
    assert token == "new_access"
    assert spotify_auth._access_token == "new_access"


@pytest.mark.asyncio
async def test_ensure_token_no_refresh(spotify_auth):
    spotify_auth._access_token = "valid"
    spotify_auth.expires_in = time.time() + 3600
    token = await spotify_auth.ensure_token()
    assert token == "valid"


@pytest.mark.asyncio
async def test_ensure_token_unauthenticated(spotify_auth):
    spotify_auth._access_token = None
    with pytest.raises(UserNotAuthenticatedException):
        await spotify_auth.ensure_token()
