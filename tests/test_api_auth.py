from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.cifra_spotify.api.routers.auth import router
from src.cifra_spotify.app.schemas.auth_schema import LoginUrl


@pytest.fixture
def app():
    """Cria app FastAPI apenas com o router de auth."""
    app = FastAPI()
    app.state.client = AsyncClient()
    app.include_router(router)
    return app


@pytest.fixture
def mock_spotify_auth(monkeypatch):
    """
    Mock da dependência SPOTIFY_AUTH.
    Substitui a função Dependency → retorna objeto falso.
    """
    mock = MagicMock()
    mock.get_login_url.return_value = "https://accounts.spotify.com/mock-login"

    # Path deve ser o exato onde SPOTIFY_AUTH é usado
    monkeypatch.setattr("src.cifra_spotify.api.deps.SPOTIFY_AUTH", lambda: mock)

    return mock


@pytest.mark.asyncio
async def test_login_endpoint_returns_correct_structure(app, mock_spotify_auth):
    """Testa se o endpoint retorna o modelo LoginUrl corretamente."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/auth/login")

    assert response.status_code == 200

    data = response.json()

    # Estrutura básica
    assert "login_url" in data
    assert "app" in data

    # Valores
    assert "https://accounts.spotify.com/authorize" in data["login_url"]
    assert data["app"] == "spotify"


@pytest.mark.asyncio
async def test_login_url_validates_model(app, mock_spotify_auth):
    """Valida se o model LoginUrl aceita os dados retornados."""
    url = "https://accounts.spotify.com/mock-login"
    model = LoginUrl(login_url=url)

    assert model.login_url == url
    assert model.app == "spotify"
