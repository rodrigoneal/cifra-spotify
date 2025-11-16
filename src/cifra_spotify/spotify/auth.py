import os
import time
import urllib.parse

from src.cifra_spotify.app.custom_exceptions.exceptions import UserNotAuthenticatedException
import httpx

from src.cifra_spotify.app.core.logger import logger


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
        logger.info("Saving token to file...")
        with open(self.TOKEN_FILE, "w") as f:
            f.write(f"{self.access_token}\n{self.refresh_token}\n{self.expires_at}")

    def _load_from_file(self):
        logger.info("Loading token from file...")
        if not os.path.exists(self.TOKEN_FILE):
            logger.info("Token file not found.")
            return

        with open(self.TOKEN_FILE, "r") as f:
            lines = f.read().strip().split("\n")
            if len(lines) == 3:
                self.access_token = lines[0]
                self.refresh_token = lines[1]
                self.expires_at = float(lines[2])

        logger.info("Token loaded from file.")

    def get_login_url(
        self, scopes: str = "user-read-currently-playing user-read-playback-state"
    ):
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": scopes,
        }
        logger.debug("Generating login URL...")
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
        logger.info("Exchanging code for token...")

        data = resp.json()
        self.access_token = data["access_token"]
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        self.expires_at = time.time() + data["expires_in"]

        self._save_to_file()
        logger.info("Tokens obtained.")
        return data

    async def refresh_access_token(self):
        logger.info("Refreshing access token...")
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
        if resp.status_code != 200:
            logger.error("Failed to refresh access token.")
            raise Exception("Failed to refresh access token.")

        logger.info("Access token refreshed.")

        data = resp.json()
        self.access_token = data["access_token"]
        self.expires_at = time.time() + data["expires_in"]

        if data.get("refresh_token"):
            self.refresh_token = data["refresh_token"]

        self._save_to_file()
        return data

    async def ensure_token(self):
        logger.debug("Ensuring access token...")
        if not self.access_token:
            logger.error("User not authenticated.")
            raise UserNotAuthenticatedException("User not authenticated.", 401)

        if time.time() >= self.expires_at - 5:
            logger.info("Access token expired. Refreshing...")
            await self.refresh_access_token()
            logger.info("Access token refreshed.")

        logger.debug("Access token obtained.")

        return self.access_token
