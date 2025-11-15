import httpx

from .auth import SpotifyAuth


class SpotifyAPI:
    BASE_URL = "https://api.spotify.com/v1"

    def __init__(self, auth: SpotifyAuth, request_timeout: int = 10):
        self.auth = auth
        self.request_timeout = request_timeout

    async def _send_request(self, path, params=None) -> httpx.Response:
        token = await self.auth.ensure_token()

        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            return await client.get(
                f"{self.BASE_URL}/{path}",
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )

    async def me(self) -> httpx.Response:
        return await self._send_request("me")

    async def get_current_track(self) -> httpx.Response:
        return await self._send_request("me/player/currently-playing")

    async def search_track(self, name: str, limit=10):
        params = {"q": name, "type": "track", "limit": limit}
        data = await self._send_request("search", params=params)

        tracks = data.get("tracks", {}).get("items", [])

        return [
            {
                "musica": t["name"],
                "artista": ", ".join(a["name"] for a in t["artists"]),
                "album": t["album"]["name"],
                "id": t["id"],
            }
            for t in tracks
        ]

    async def get_my_playlists(
        self, limit: int = 10, offset: int = 0
    ) -> httpx.Response:
        token = await self.auth.ensure_token()

        async with httpx.AsyncClient() as client:
            params = {"limit": limit, "offset": offset}
            return await client.get(
                "https://api.spotify.com/v1/me/playlists",
                headers={"Authorization": f"Bearer {token}"},
                params=params,
            )

    async def search_playlist(
        self, name: str, limit: int = 10, offset: int = 0
    ) -> httpx.Response:
        token = await self.auth.ensure_token()

        async with httpx.AsyncClient() as client:
            return await client.get(
                "https://api.spotify.com/v1/search",
                params={
                    "q": name,
                    "type": "playlist",
                    "limit": limit,
                    "offset": offset,
                },
                headers={"Authorization": f"Bearer {token}"},
            )
