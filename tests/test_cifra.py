from pathlib import Path
import pytest

from src.cifra_spotify.cifras.cifra_base import Instruments
from src.cifra_spotify.cifras.cifra_club import CifraClub




@pytest.mark.asyncio
async def test_se_pega_a_cifra_cifra_club():
    cifra_club = CifraClub()
    cifra = await cifra_club.get_cifra(
        "Arlindo Cruz", "Trilha do Amor", Instruments.GUITAR
    )
    assert "A#m6" in cifra["cifra"]



@pytest.mark.asyncio
async def test_se_pega_a_cifra_pdf():
    cifra_club = CifraClub()
    cifra = await cifra_club.to_pdf(
        "Arlindo Cruz", "Trilha do Amor", Instruments.CAVACO, tabs=False
    )
    assert cifra.startswith(b"%PDF-1.7")
