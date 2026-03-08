from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class ChordMetadata(BaseModel):
    has_html_formatting: bool = Field(
        ..., description="Indica se a cifra contém formatação HTML."
    )
    has_lyrics: bool = Field(
        ..., description="Indica se a cifra contém letra da música."
    )
    has_chords: bool = Field(..., description="Indica se a cifra contém acordes.")


class ChordResult(BaseModel):
    id: Optional[str] = Field(
        default=None, description="Identificador único opcional do resultado."
    )
    title: str = Field(..., description="Título da música.")
    artist: Optional[str] = Field(default=None, description="Nome do artista ou banda.")
    artist_spotify_id: Optional[str] = Field(
        default=None, description="ID do artista no Spotify."
    )
    genres: Optional[List[str]] = Field(
        default=None, description="Genres artist or band."
    )
    key: Optional[str] = Field(default=None, description="Tom da música.")
    instrument: Optional[str] = Field(
        default="guitar", description="Instrumento referente à cifra."
    )
    source: Optional[str] = Field(
        default=None, description="Fonte de onde a cifra foi obtida."
    )
    url: HttpUrl = Field(..., description="URL da cifra original.")
    preview: Optional[str] = Field(
        default=None, description="Trecho resumido da cifra para exibição em listas."
    )
    metadata: ChordMetadata = Field(
        ..., description="Metadados sobre o conteúdo da cifra."
    )


class ChordSearchResponse(BaseModel):
    success: bool = Field(
        ..., description="Indica se a busca foi realizada com sucesso."
    )
    count: int = Field(..., description="Quantidade de resultados encontrados.")
    results: List[ChordResult] = Field(
        default_factory=list, description="Lista de cifras encontradas."
    )
