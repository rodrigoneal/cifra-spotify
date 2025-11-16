import httpx

from src.cifra_spotify.app.core.config import settings


async def notify_change(track: dict):
    data = {
        "name": track["name"],
        "artist": track["artists"][0]["name"],
        "id": track["id"],
    }

    async with httpx.AsyncClient() as client:
        await client.post(
            settings.SPOTIFY_WEBHOOK_URL,
            json=data,
        )
