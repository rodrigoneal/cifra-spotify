# 🎵 Cifra Spotify API

API em FastAPI para buscar músicas que estão tocando no Spotify,
pesquisar playlists e obter todas as músicas de uma playlist ---
possibilitando futuramente integrar e retornar cifras automaticamente.

## 📌 Objetivo do Projeto

Este projeto tem como objetivo:

-   Obter a música que o usuário está ouvindo atualmente no Spotify
-   Buscar playlists pelo nome.
-   Listar todas as playlists do usuário autenticado.
-   Obter todas as músicas de qualquer playlist.
-   Integrar com um sistema externo de cifras (como CifraClub,
    Cifras e BananaCifras).
-   Download PDF da cifra.
-   Sincronizar musica tocando no spotify com a cifra.
-   Criar PDF com todas as cifras de uma playlist.
-   Criar um fluxo completo para retornar nome da música + artista +
    cifra

## 🚀 Tecnologias Utilizadas

-   FastAPI\
-   Python 3.10+\
-   Pydantic v2\
-   httpx\
-   OAuth 2.0 (Spotify)\
-   Docker (opcional)

## 🔐 Autenticação -- Spotify OAuth

Configure no arquivo `.env`:

    SPOTIFY_CLIENT_ID=xxxx
    SPOTIFY_CLIENT_SECRET=xxxx
    SPOTIFY_REDIRECT_URI=https://seu-dominio.com/webhooks/callback/

E no painel do Spotify Developer:

-   Dashboard → Edit Settings → Redirect URIs\
-   Adicione exatamente o mesmo valor do `.env`

## 🔥 Endpoints Disponíveis

### 🎧 1. Música atual do Spotify

`GET /api/current_track`

### 🔎 2. Buscar playlists por nome

`GET /api/playlist/search_playlist`

### 📚 3. Listar playlists do usuário

`GET /api/playlist/my_playlists`

## 🧪 Como executar

    poetry run fastapi run main.py

Acesse a documentação: `http://0.0.0.1:8000/docs`

## 📌 Roadmap

-   [x] Buscar música atual\
-   [x] Buscar playlists\
-   [x] Listar playlists do usuário\
-   [ ] Buscar faixas de uma playlist\
-   [x] Sistema de cifras\
-   [ ] Interface Web
## 📝 Contribua

-   [ ] Adicionar documentação
-   [ ] Adicionar interface Web
-   [ ] Adicionar sistema de cifras
-   [ ] Adicionar testes
-   [ ] Adicionar Docker
-   [ ] Adicionar CI/CD
-   [ ] Adicionar deploy
-   [ ] Adicionar logger


## Disclaimer

Esse projeto foi desenvolvido com o intuito de aprendizado e
desenvolvimento pessoal.

Meu objetivo principal é só atender uma demanda pessoal que estou aprendendo a tocar banjo e preciso ficar sempre procurando a musica que está tocando no spotify nos sites de cifras.

Não tenho a pretenção de sincronizar o tempo da musica com a cifra como faz o site Ultimate Guitar ou algo similar.

Acabei me empolgando e criando rotas para o spotify que não tem nada a ver com o meu objetivo primario, mas é bom que fica caso alguém precise do spotify para algo.