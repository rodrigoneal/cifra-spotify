import os
import time
import urllib.parse

import httpx


class SpotifyAuth:
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    TOKEN_FILE = ".spotify_token"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

        self.access_token = None
        self.refresh_token = None
        self.expires_at = None

        self._load_from_file()

    def _save_to_file(self):
        with open(self.TOKEN_FILE, "w") as f:
            f.write(f"{self.access_token}\n{self.refresh_token}\n{self.expires_at}")

    def _load_from_file(self):
        if not os.path.exists(self.TOKEN_FILE):
            return

        with open(self.TOKEN_FILE, "r") as f:
            lines = f.read().strip().split("\n")
            if len(lines) == 3:
                self.access_token = lines[0]
                self.refresh_token = lines[1]
                self.expires_at = float(lines[2])

    def get_login_url(
        self, scopes: str = "user-read-currently-playing user-read-playback-state"
    ):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": scopes,
        }
        return f"{self.AUTH_URL}?{urllib.parse.urlencode(params)}"

    async def exchange_code_for_token(self, code: str):
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        self.expires_at = time.time() + data["expires_in"]

        self._save_to_file()
        return data

    async def refresh_access_token(self):
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

        data = resp.json()
        self.access_token = data["access_token"]
        self.expires_at = time.time() + data["expires_in"]

        if data.get("refresh_token"):
            self.refresh_token = data["refresh_token"]

        self._save_to_file()
        return data

    async def ensure_token(self):
        if not self.access_token:
            raise Exception("Usuário não autenticado.")

        if time.time() >= self.expires_at - 5:
            await self.refresh_access_token()

        return self.access_token
