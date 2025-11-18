import json
from pathlib import Path

import aiofiles
import aiofiles.os
from cryptography.fernet import Fernet, InvalidToken

from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.schemas.auth_schema import SpotifyToken


class SpotifyTokenStorage:
    """
    Async + encrypted token storage using Fernet.

    - Uses aiofiles for async disk I/O
    - Encrypts all data at rest with Fernet
    """

    def __init__(self, filepath: str | Path, key: str):
        self.filepath = Path.home() / Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self.cipher = Fernet(key.encode("utf-8"))

    async def load(self) -> SpotifyToken | None:
        logger.info(f"Loading token from {self.filepath}")
        if not self.filepath.exists():
            return None

        try:
            async with aiofiles.open(self.filepath, "rb") as f:
                encrypted = await f.read()
            decrypted = self.cipher.decrypt(encrypted)
            data = json.loads(decrypted.decode("utf-8"))
            return SpotifyToken(**data)

        except (InvalidToken, ValueError, json.JSONDecodeError):
            # Arquivo inválido ou corrompido → ignorar
            return None

        except Exception:
            return None  # pode logar se quiser

    async def save(self, token: SpotifyToken) -> None:
        raw_json = token.model_dump_json().encode("utf-8")
        encrypted = self.cipher.encrypt(raw_json)

        async with aiofiles.open(self.filepath, "wb") as f:
            await f.write(encrypted)

    async def clear(self) -> None:
        if self.filepath.exists():
            await aiofiles.os.remove(self.filepath)
