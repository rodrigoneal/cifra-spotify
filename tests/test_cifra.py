import asyncio
import pytest
import httpx

from src.cifra_spotify.cifras.cifra_club import CifraClub, divisor_medley_default
from src.cifra_spotify.cifras.cifra_base import Instruments

from src.cifra_spotify.cifras.parsers.cifraclub import parse_cifra_page
from src.cifra_spotify.cifras.render.cifraclub import render_html_document




def test_divisor_medley_default():
    assert divisor_medley_default("A/B/C") == ["A", "B", "C"]
    assert divisor_medley_default("ABC") == ["ABC"]
    assert divisor_medley_default("A - B", divisor=" - ") == ["A", "B"]


def test_build_url(monkeypatch):
    cifra = CifraClub()
    url = cifra._build_url("ExaltaSamba", "Tá Vendo Aquela Lua", Instruments.GUITAR)

    assert url == "exaltasamba/ta-vendo-aquela-lua/#instrument=guitar"

@pytest.mark.asyncio
async def test_fetch_page(monkeypatch):
    async def mock_send(request):
        return httpx.Response(200, text="<html>ok</html>")

    transport = httpx.MockTransport(mock_send)

    cifra = CifraClub()
    cifra.client = httpx.AsyncClient(transport=transport)

    response = await cifra._fetch_page("exaltasamba/lua")

    assert response.status_code == 200
    assert "<html>" in response.text

@pytest.mark.asyncio
async def test_fetch_cifra(monkeypatch):

    async def mock_fetch_page(*args, **kwargs):
        return httpx.Response(
            200, text="<div class='cifra'>OK</div><h1 class='t1'>Lua</h1><pre>OK</pre>"
        )

    monkeypatch.setattr(CifraClub, "_fetch_page", mock_fetch_page)
    monkeypatch.setattr(
        "src.cifra_spotify.cifras.parsers.cifraclub.parse_cifra_page",
        lambda response, tabs: {"ok": True, "tabs": tabs},
    )

    cifra = CifraClub()
    result = await cifra._fetch_cifra("Exalta", "Lua", True)

    assert result == {"tom": "", "cifra": "<pre>OK</pre>", "music_name": "Lua"}


@pytest.mark.asyncio
async def test_generate_html(monkeypatch):
    """Mock _fetch_cifra + render_html_document"""

    async def fake_fetch_cifra(*args, **kwargs):
        return {"music_name": "Lua", "tom": "", "cifra": "<pre>OK</pre>"}

    monkeypatch.setattr(CifraClub, "_fetch_cifra", fake_fetch_cifra)

    monkeypatch.setattr(
        "src.cifra_spotify.cifras.render.cifraclub.render_html_document",
        lambda cifras: f"<html>{len(cifras)}</html>",
    )

    cifra = CifraClub()
    html = await cifra.generate_html(
        singer="exaltasamba", music="lua", tabs=True, instrument=Instruments.GUITAR
    )

    assert "<pre>OK</pre>" in html


@pytest.mark.asyncio
async def test_generate_pdf(monkeypatch):
    """Mock do _generate_pdf para não precisar criar PDF real"""

    monkeypatch.setattr(CifraClub, "_generate_pdf", lambda self, html: b"%PDF-1.4 mock")

    cifra = CifraClub()
    pdf_bytes = await cifra.generate_pdf("<html></html>")

    assert pdf_bytes.startswith(b"%PDF")
