import httpx
import pytest
import pytest_asyncio

from src.cifra_spotify.cifras.cifra_base import Instruments
from src.cifra_spotify.cifras.cifra_club.cifra_club import CifraClub


@pytest_asyncio.fixture
async def client():
    async with httpx.AsyncClient() as async_client:
        yield async_client


@pytest_asyncio.fixture()
async def cifra_club(client: httpx.AsyncClient):
    return CifraClub(client)


@pytest.mark.asyncio
async def test_se_pega_a_cifra_do_cifra_club(cifra_club: CifraClub):
    cifra = await cifra_club.fetch("Exaltasamba", "gamei", True, Instruments.GUITAR)
    assert cifra[0].music_name.lower() == "gamei"
    assert "Que as nuvens do céu".lower() in cifra[0].cifra.lower()


@pytest.mark.asyncio
async def test_se_pega_a_cifra_medley_do_que_tem_completo_no_cifra_club(
    cifra_club: CifraClub,
):
    cifra = await cifra_club.fetch(
        "Pericles",
        "40 graus/ gamei/ azul sem fim/ até o sol quis ver/ a carta",
        False,
        Instruments.GUITAR,
    )
    assert (
        "40 Graus / Gamei/ Azul Sem Fim / Até o Sol Quis Ver / A Carta ".lower()
        in cifra[0].music_name.lower()
    )
    assert "É só você entrar aqui é seu lugar".lower() in cifra[0].cifra.lower()
    assert "Minha paixão é você".lower() in cifra[0].cifra.lower()


@pytest.mark.asyncio
async def test_se_pega_a_cifra_medley_do_cifra_club(cifra_club: CifraClub):
    cifra = await cifra_club.fetch(
        "Pericles",
        "Até que durou / melhor eu ir",
        False,
        Instruments.GUITAR,
    )
    assert isinstance(cifra, list)
    assert len(cifra) == 2


@pytest.mark.asyncio
async def test_se_pega_cifra_inexistente_do_cifra_club(cifra_club: CifraClub):
    with pytest.raises(ValueError):
        await cifra_club.fetch(
            "Cantor Inexistente", "Musica Inexistente", True, Instruments.GUITAR
        )
