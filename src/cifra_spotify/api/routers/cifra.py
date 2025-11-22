import io

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.cifra_spotify.api.deps import CIFRACLUB

router = APIRouter(prefix="/cifra", tags=["cifra"])


class CifraRequestSchema(BaseModel):
    cantor: str
    musica: str
    genero: str | None = None


@router.post("/search/")
async def search_cifras(cifra_request: CifraRequestSchema, cifra_club: CIFRACLUB):
    result = await cifra_club.fetch(
        cifra_request.cantor, cifra_request.musica, tabs=False
    )
    headers = {
        "Content-Disposition": f'inline; filename="{cifra_request.cantor}_{cifra_request.musica}.pdf"',
        "content-type": "application/octet-stream",
    }
    pdf_bytes = await result.to_pdf()
    return StreamingResponse(
        io.BytesIO(pdf_bytes), media_type="application/pdf", headers=headers
    )
