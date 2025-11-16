import pytest

from src.cifra_spotify.cifras.cifra_base import Instruments
from src.cifra_spotify.cifras.cifra_club import CifraClub


@pytest.mark.asyncio
async def test_se_pega_a_cifra_cifra_club():
    cifra_club = CifraClub()
    cifra = await cifra_club.generate_html(
        "Arlindo Cruz", "Trilha do Amor", Instruments.GUITAR
    )
    assert "A#m6" in cifra


@pytest.mark.asyncio
async def test_se_pega_a_cifra_pdf():
    cifra_club = CifraClub()
    html = await cifra_club.generate_html(
        "Arlindo Cruz", "Trilha do Amor", Instruments.CAVACO, tabs=True
    )
    pdf = await cifra_club.generate_pdf(html)
    assert pdf.startswith(b"%PDF-1.7")
    with open("test.pdf", "wb") as file:
        file.write(pdf)


@pytest.mark.asyncio
async def test_se_pega_a_cifra_pdf_com_tabs():
    cifra_club = CifraClub()
    cifra = await cifra_club.generate_html(
        "Arlindo Cruz", "Trilha do Amor", Instruments.CAVACO, tabs=True
    )
    assert "B|-3--5" in cifra


@pytest.mark.asyncio
async def test_se_traz_as_cifras_do_medley():
    cifra_club = CifraClub()
    cifra = await cifra_club.generate_html(
        "ExaltaSamba musicas",
        "Gamei/ Azul Sem Fim / Até o Sol Quis Ver / A Carta",
        Instruments.CAVACO,
        tabs=False,
    )
    pdf = await cifra_club.generate_pdf(cifra)
    with open("test.pdf", "wb") as file:
        file.write(pdf)
