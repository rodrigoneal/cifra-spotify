from fastapi import APIRouter

router = APIRouter(prefix="/api/cifra", tags=["CIFRA"])


@router.get("/")
async def cifra():
    return
