import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from src.cifra_spotify.spotify.pooling import SpotifyPollingService
from src.cifra_spotify.spotify.spotify import SpotifyAPI


@pytest.mark.asyncio
async def test_tick_no_track_playing_resets_current_track_id():
    """Deve resetar _current_track_id e disparar stop quando não há música."""
    api = MagicMock(spec=SpotifyAPI)
    api.get_current_track = AsyncMock(return_value=MagicMock(status_code=204))

    hook_called = []

    def on_stop(event):
        hook_called.append(event)

    service = SpotifyPollingService(api, on_track_stop=on_stop)
    service._current_track_id = "123"

    await service._tick()

    assert service._current_track_id is None
    assert len(hook_called) == 1
    assert hook_called[0]["id"] == "123"
    assert hook_called[0]["progress_ms"] is None


@pytest.mark.asyncio
async def test_tick_first_track_triggers_start_hook():
    """Deve disparar hook start e webhook na primeira música."""
    fake_track = {"id": "1", "name": "Song", "artists": [{"name": "Artist"}]}
    response = MagicMock(status_code=200)
    response.json.return_value = {"item": fake_track, "progress_ms": 1000}

    api = MagicMock(spec=SpotifyAPI)
    api.get_current_track = AsyncMock(return_value=response)

    hook_called = []

    def on_start(event):
        hook_called.append(event)

    service = SpotifyPollingService(api, on_track_start=on_start, webhook_url=None)

    await service._tick()

    assert service._current_track_id == "1"
    assert len(hook_called) == 1
    assert hook_called[0]["id"] == "1"
    assert hook_called[0]["progress_ms"] == 1000


@pytest.mark.asyncio
async def test_tick_track_change_triggers_change_hook():
    """Quando a música muda, deve disparar change hook."""
    fake_track = {"id": "2", "name": "New Song", "artists": [{"name": "Artist"}]}
    response = MagicMock(status_code=200)
    response.json.return_value = {"item": fake_track, "progress_ms": 500}

    api = MagicMock(spec=SpotifyAPI)
    api.get_current_track = AsyncMock(return_value=response)

    hook_called = []

    def on_change(event):
        hook_called.append(event)

    service = SpotifyPollingService(
        api, on_track_change=on_change, webhook_url=None
    )
    service._current_track_id = "1"

    await service._tick()

    assert service._current_track_id == "2"
    assert len(hook_called) == 1
    assert hook_called[0]["id"] == "2"
    assert hook_called[0]["progress_ms"] == 500


@pytest.mark.asyncio
async def test_fire_supports_async_hooks():
    """Hooks assíncronos e síncronos devem funcionar."""
    hook_sync_called = []
    hook_async_called = []

    def hook_sync(event):
        hook_sync_called.append(event)

    async def hook_async(event):
        hook_async_called.append(event)

    service = SpotifyPollingService(MagicMock(spec=SpotifyAPI))
    hooks = [hook_sync, hook_async]

    await service._fire(hooks, {"id": "1"})

    assert len(hook_sync_called) == 1
    assert len(hook_async_called) == 1
    assert hook_sync_called[0]["id"] == "1"
    assert hook_async_called[0]["id"] == "1"


@pytest.mark.asyncio
async def test_notify_webhook_post_called():
    """Deve chamar _http.post com payload correto."""
    fake_track = {"id": "1", "name": "Song", "artists": [{"name": "Artist"}], "progress_ms": 123}

    api = MagicMock(spec=SpotifyAPI)
    api.get_current_track = AsyncMock()

    service = SpotifyPollingService(api, webhook_url="http://example.com")

    with patch.object(service._http, "post", new_callable=AsyncMock) as post:
        await service._notify_webhook(fake_track)

    post.assert_awaited_once_with("http://example.com", json=fake_track)
