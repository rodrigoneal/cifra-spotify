from typing import Annotated

from fastapi import APIRouter, Query
from pydantic import BaseModel

from src.cifra_spotify.api.deps import SPOTIFY_AUTH
from src.cifra_spotify.app.core.logger import logger

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class ResponseWebhook(BaseModel):
    status: str


@router.get("/callback", response_model=ResponseWebhook)
async def spotify_webhook(
    spotify_auth: SPOTIFY_AUTH,
    code: Annotated[str, Query(description="token de acesso")],
) -> None:
    try:
        await spotify_auth.exchange_code_for_token(code)
        logger.info("Token de acesso obtido")
        return {"status": "ok"}
    except Exception as e:
        logger.error(e)
        return {"status": "error"}
