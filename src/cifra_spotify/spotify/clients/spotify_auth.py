from __future__ import annotations

import json
import time
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.cifra_spotify.spotify.clients.spotify_token_storage import (
        SpotifyTokenStorage,
    )

import httpx

from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.custom_exceptions.exceptions import (
    SpotifyAuthException,
    UserNotAuthenticatedException,
)
from src.cifra_spotify.app.schemas.auth_schema import SpotifyToken


class SpotifyAuth:
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    TOKEN_FILE = Path.home() / ".cifra_spotify" / "token.enc"
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    TOKEN_EXPIRATION_BUFFER = 60

    def __init__(
        self,
        client: httpx.AsyncClient,
        storage: "SpotifyTokenStorage",
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ):
        self.client = client
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        self.access_token = None
        self.refresh_token = None
        self.expires_in = None
        self.storage: SpotifyTokenStorage = storage

    async def init(self):
        data = await self.storage.load()
        if data:
            self.access_token = data.access_token
            self.refresh_token = data.refresh_token
            self.expires_in = data.expires_in

    def get_login_url(
        self, scopes: str = "user-read-currently-playing user-read-playback-state"
    ):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": scopes,
        }
        logger.debug("[SpotifyClient] Gerando URL de login...")
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def exchange_code_for_token(self, code: str) -> SpotifyToken:
        resp = await self.client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        logger.debug("[SpotifyClient] Mudando code para token...")

        if resp.status_code != 200:
            msg = f"[SpotifyClient] Falha ao mudar code para token: {resp.status_code}"
            logger.error(msg)
            raise SpotifyAuthException(msg)
        try:
            content = await resp.aread()
            data = json.loads(content)
            self.access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            self.expires_in = time.time() + data["expires_in"]
            token = SpotifyToken(**data)
            await self.storage.save(token)
            logger.debug("[SpotifyClient] Token obtido.")
            return token
        except KeyError as e:
            msg = f"[SpotifyClient] Falha ao abrir token: {e}"
            logger.error(msg)
            raise SpotifyAuthException(msg)
        except Exception as e:
            msg = f"[SpotifyClient] Falha inesperada ao abrir token: {e}"
            logger.error(msg)
            raise SpotifyAuthException(msg)

    async def refresh_access_token(self) -> SpotifyToken:
        logger.info("[SpotifyClient] Atualizando acesso ao token...")

        resp = await self.client.post(
            self.TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        if resp.status_code != 200:
            msg = f"[SpotifyClient] Falha ao atualizar acesso ao token: {resp.status_code}: {resp.text}"
            logger.error(msg)
            raise SpotifyAuthException(msg)

        content = await resp.aread()
        data = json.loads(content)
        self.access_token = data["access_token"]
        self.expires_in = time.time() + data["expires_in"]

        if data.get("refresh_token"):
            self.refresh_token = data["refresh_token"]
        if not data.get("refresh_token"):
            data["refresh_token"] = self.refresh_token
        token = SpotifyToken(**data)
        await self.storage.save(token)
        logger.debug("[SpotifyClient] Acesso ao token atualizado...")
        return token

    async def ensure_token(self) -> str:
        logger.debug("[SpotifyClient] Garantindo acesso ao token...")
        if not self.access_token:
            logger.error("Usuario não autenticado.")
            raise UserNotAuthenticatedException("Usuario não autenticado.", 401)

        if time.time() >= self.expires_in - self.TOKEN_EXPIRATION_BUFFER:
            logger.debug("[SpotifyClient] Token de acesso expirado. Atualizando...")
            await self.refresh_access_token()
            logger.debug("[SpotifyClient] Token de acesso atualizado.")

        logger.debug("[SpotifyClient] Token de acesso garantido.")

        return self.access_token
