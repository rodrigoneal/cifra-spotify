import asyncio
import inspect
from typing import Callable

import httpx

from cifra_spotify.app.core.config import settings
from src.cifra_spotify.app.core.logger import logger
from src.cifra_spotify.app.custom_exceptions.exceptions import (
    UserNotAuthenticatedException,
)
from src.cifra_spotify.spotify.clients.spotify import Spotify

HOOKSTYPE = Callable[[dict], None]

EVENT_TYPES = ("start", "change", "stop")


class SpotifyPollingService:
    """
    Serviço de polling do Spotify.

    EVENTOS DISPONÍVEIS:

    • "start"  → disparado quando a primeira música começa a tocar.
    • "change" → disparado quando o usuário troca de música.
    • "stop"   → disparado quando a música para de tocar.

    Todos os eventos recebem um dicionário com:

    {
        "id": "track_id",
        "name": "Nome da música",
        "artist": "Artista principal",
        "progress_ms": 123456   # tempo atual da música em milissegundos
    }
    """

    def __init__(
        self,
        api: Spotify,
        interval: int = 3,
        max_interval: int = 10,
        on_track_change=None,
        on_track_stop=None,
        on_track_start=None,
        webhook_url: str | None = None,
    ):
        self.api = api
        self.interval = interval
        self._interval = interval
        self.max_interval = max_interval
        self.on_track_change = self._ensure_list(on_track_change)
        self.on_track_stop = self._ensure_list(on_track_stop)
        self.on_track_start = self._ensure_list(on_track_start)
        self.webhook_url = webhook_url or settings.SPOTIFY_WEBHOOK_URL

        self._current_track_id: str | None = None
        self._running = False
        self._task: asyncio.Task | None = None
        self._http = httpx.AsyncClient(timeout=10)

    @staticmethod
    def _ensure_list(value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [value]

    async def start(self):
        logger.info("[Polling] Starting...")
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        logger.info("[Polling] Stopping polling loop...")
        self._running = False

        if self._task:
            self._task.cancel()

        await self._http.aclose()

    async def _run(self):
        logger.info("[Polling] Started.")
        while self._running:
            try:
                await self._tick()
            except UserNotAuthenticatedException as exc:
                logger.error(f"[Polling] Error: {exc}", exc_info=True)
                self._interval = self.max_interval
            except Exception as exc:
                logger.error(f"[Polling] Error: {exc}", exc_info=True)
            logger.debug(f"[Polling] Waiting {self._interval}s...")
            await asyncio.sleep(self._interval)

    async def _tick(self):
        logger.debug("[Polling] Ticking...")
        response = await self.api.get_current_track()

        if response.status_code == 204:
            logger.debug("[Polling] No track playing.")
            self._interval = min(self._interval * 2, self.max_interval)
            logger.debug(
                f"[Polling] Music stopped → increasing interval to {self._interval}s"
            )

            if self._current_track_id is not None:
                # Aumentar o tempo de espera do polling

                logger.info("[Polling] Track stopped.")
                await self._fire(
                    self.on_track_stop,
                    {"id": self._current_track_id, "progress_ms": None},
                )

                self._current_track_id = None
            return

        if self._interval != self.interval:
            logger.info(
                f"[Polling] Music playing again → resetting interval to {self.interval}s"
            )
        self._interval = self.interval

        data = response.json()
        track = data.get("item")
        progress_ms = data.get("progress_ms")
        if not track:
            return

        track_id = track.get("id")

        event_payload = {
            "id": track_id,
            "name": track["name"],
            "artist": track["artists"][0]["name"],
            "progress_ms": progress_ms,
        }

        # Primeira música tocando
        if not self._current_track_id:
            logger.info("[Polling] First track playing.")
            self._current_track_id = track_id

            await self._fire(self.on_track_start, event_payload)
            await self._notify_webhook(event_payload)
            return

        # Troca de música
        if track_id != self._current_track_id:
            logger.info("[Polling] Track changed.")
            self._current_track_id = track_id

            await self._fire(self.on_track_change, event_payload)
            await self._notify_webhook(event_payload)

    async def _notify_webhook(self, payload: dict):
        logger.info("[Webhook] Notifying...")
        if not self.webhook_url:
            return

        try:
            await self._http.post(self.webhook_url, json=payload)
            logger.info("[Webhook] Event sent.")
        except Exception as exc:
            logger.error(f"[Webhook] Error: {exc}", exc_info=True)

    def add_hook(self, event: str, callback: HOOKSTYPE):
        """
        Registra um callback para um dos eventos:

        • "start"  → música começou
        • "change" → trocou de música
        • "stop"   → música parou
        """
        if event not in EVENT_TYPES:
            raise ValueError(
                f"Unknown event '{event}'. Use one of: {', '.join(EVENT_TYPES)}"
            )

        if event == "start":
            self.on_track_start.append(callback)
        elif event == "change":
            self.on_track_change.append(callback)
        elif event == "stop":
            self.on_track_stop.append(callback)

    async def _fire(self, hooks: list[HOOKSTYPE], data: dict):
        """
        Dispara um hook.

        Args:
            hooks (list[HOOKSTYPES]): Lista de hooks a serem disparados.
            data (dict): Dados para o hook.
        """
        for hook in hooks:
            await self._fire_async(hook, data)

    async def _fire_async(self, hook, data, timeout=5):
        try:
            if inspect.iscoroutinefunction(hook):
                await hook(data)
            else:
                await asyncio.wait_for(asyncio.to_thread(hook, data), timeout)
        except Exception as e:
            logger.error(f"Hook error: {e}", exc_info=True)
