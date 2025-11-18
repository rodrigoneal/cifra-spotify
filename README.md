[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/rodrigoneal)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/rodrigo-silva-de-castro/)


# 🎵 Cifra Spotify

Uma aplicação que integra Spotify com provedores de cifras para gerar
cifras automaticamente da música que está tocando --- incluindo suporte
futuro para medleys, PDFs e diagramas de acordes.

## 🚀 Funcionalidades

-   Login via OAuth com Spotify\
-   Obter música atual tocando\
-   Buscar cifras automaticamente em múltiplos provedores\
-   Em breve: mudança automática da cifra conforme transições de medley\
-   Gerar PDF da cifra da música atual\
-   Gerar PDF de playlists inteiras para tocar sem internet\
-   Planejado: diagramas automáticos de acordes

## 🎸 Provedores de Cifras (atuais e planejados)

-   **CifraClub** (inicial)
-   **BananaCifras**
-   **Cifras.com.br**

**Possíveis integrações futuras:**

-   Ultimate Guitar\
-   Songsterr\
-   Chordify\
-   E-Chords

## 🔁 Polling Inteligente

O sistema de polling vai acompanhar em tempo real:

-   Troca de música\
-   Progresso da faixa\
-   Mudança automática da cifra\
-   Pontos marcados pelo usuário em medleys (planejado)

## 📄 Geração de PDF

-   PDF da cifra de uma única música\
-   PDF de toda a playlist\
-   Ideal para tocar em locais sem internet

## 🎼 Futuro: Diagramas de Acordes

Planejado:

-   Renderização automática dos diagramas dos acordes usados\
-   Suporte para cavaquinho, violão e guitarra\
-   Formato SVG escalável

## 🛠️ Tecnologias

-   FastAPI\
-   Async/await\
-   httpx\
-   Pydantic\
-   uvloop (Linux/Mac)\

------------------------------------------------------------------------

## 📦 Instalação

``` bash
git clone https://github.com/rodrigoneal/cifra-spotify
cd cifra-spotify
cp .env.example .env
poetry install
poetry run fastapi run main.py
```

------------------------------------------------------------------------

## 📝 Licença

MIT.

------------------------------------------------------------------------

Feito com ❤️ por Rodrigo O'Neal

