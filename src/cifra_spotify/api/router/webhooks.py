from typing import Annotated

from fastapi import APIRouter, Query

from src.cifra_spotify.api.deps import SPOTIFYDEPS

router = APIRouter(prefix="/webhooks", tags=["WEBHOOKS"])


@router.get("/callback")
async def callback(code: Annotated[str, Query()], spotify: SPOTIFYDEPS):
    data = await spotify.auth.exchange_code_for_token(code)

    return {"status": "logado", "tokens": data}
