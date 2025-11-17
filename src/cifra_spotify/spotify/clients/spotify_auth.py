import asyncio
import json
import time
import urllib.parse
from pathlib import Path

import aiofiles
import aiofiles.os
import httpx
from cryptography.fernet import Fernet, InvalidToken

from src.cifra_spotify.app.core.config import settings
from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.custom_exceptions.exceptions import (
    InvalidFileFormatException,
    SpotifyAuthException,
    UserNotAuthenticatedException,
)
from src.cifra_spotify.app.schemas.token import TokenData

_file_lock = asyncio.Lock()

key = settings.TOKEN_KEY.encode("utf-8")
cipher = Fernet(key)


class SpotifyAuth:
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    TOKEN_FILE = Path.home() / ".cifra_spotify" / "token.enc"
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)

    TOKEN_EXPIRATION_BUFFER = 60

    def __init__(
        self,
        client: httpx.AsyncClient,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
    ):
        self.client = client
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        self._access_token = None
        self.refresh_token = None
        self.expires_in = None

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        raise AttributeError("Token de acesso nao pode ser atribuido diretamente.")

    async def init(self):
        await self._load_from_file()

    async def _delete_file(self):
        async with _file_lock:
            try:
                await aiofiles.os.remove(self.TOKEN_FILE)
                logger.debug(f"[SpotifyClient] Arquivo {self.TOKEN_FILE} removido.")
            except FileNotFoundError:
                logger.debug(f"[SpotifyClient] Arquivo {self.TOKEN_FILE} não existe para remover.")

    async def _save_to_file(self):
        logger.debug("[SpotifyClient] Salvando token no arquivo...")
        async with _file_lock:
            async with aiofiles.open(self.TOKEN_FILE, "wb") as f:
                await f.write(
                    cipher.encrypt(
                        f"{self.access_token}|{self.refresh_token}|{self.expires_in}".encode(
                            "utf-8"
                        )
                    )
                )

    async def _load_from_file(self) -> TokenData:
        logger.debug("[SpotifyClient] Carregando token do arquivo...")
        if not Path(self.TOKEN_FILE).exists():
            logger.error(f"Arquivo {self.TOKEN_FILE} não encontrado.")
            return
        async with _file_lock:
            async with aiofiles.open(self.TOKEN_FILE, "rb") as f:
                try:
                    content = await f.read()
                    decrypted = cipher.decrypt(content).decode().split("|")
                    lines = decrypted
                    if len(lines) == 3:
                        self._access_token = lines[0]
                        self.refresh_token = lines[1]
                        self.expires_in = float(lines[2])

                        logger.debug("[SpotifyClient] Token carregado do arquivo.")
                        return TokenData(
                            access_token=self._access_token,
                            refresh_token=self.refresh_token,
                            expires_in=self.expires_in,
                        )
                    else:
                        logger.error(f"[SpotifyClient] Arquivo {self.TOKEN_FILE} inválido.")
                        raise InvalidFileFormatException(
                            f"Arquivo {self.TOKEN_FILE} inválido."
                        )
                except (ValueError, IndexError) as exc:
                    breakpoint()
                    logger.error(f"[SpotifyClient] Arquivo {self.TOKEN_FILE} inválido.")
                    raise InvalidFileFormatException(
                        f"Arquivo {self.TOKEN_FILE} inválido."
                    )
                except InvalidToken:
                    logger.error(f"[SpotifyClient] Arquivo {self.TOKEN_FILE} inválido.")
                    raise InvalidFileFormatException(
                        f"Arquivo {self.TOKEN_FILE} inválido."
                    )
                except Exception as exc:
                    logger.error(f"[SpotifyClient] Erro ao carregar token: {exc}", exc_info=True)
                    raise SpotifyAuthException(f"Erro ao carregar token: {exc}")

        logger.debug("[SpotifyClient] Token carregado do arquivo.")

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

    async def exchange_code_for_token(self, code: str) -> TokenData:
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
            self._access_token = data["access_token"]
            self.refresh_token = data.get("refresh_token", self.refresh_token)
            self.expires_in = time.time() + data["expires_in"]
        except KeyError as e:
            msg = f"[SpotifyClient] Falha ao abrir token: {e}"
            logger.error(msg)
            raise SpotifyAuthException(msg)
        except Exception as e:
            msg = f"[SpotifyClient] Falha inesperada ao abrir token: {e}"
            logger.error(msg)
            raise SpotifyAuthException(msg)

        await self._save_to_file()
        logger.debug("[SpotifyClient] Token obtido.")
        return TokenData(**data)

    async def refresh_access_token(self) -> TokenData:
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
        self._access_token = data["access_token"]
        self.expires_in = time.time() + data["expires_in"]

        if data.get("refresh_token"):
            self.refresh_token = data["refresh_token"]

        await self._save_to_file()
        logger.debug("[SpotifyClient] Acesso ao token atualizado...")
        return TokenData(**data)

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
