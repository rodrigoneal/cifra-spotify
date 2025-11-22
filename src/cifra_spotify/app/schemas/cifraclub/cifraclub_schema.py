from dataclasses import dataclass


@dataclass(frozen=True)
class CifraTransportSchema:
    cifra: str
    tom: str
    music_name: str
    tablatura: str | None = None
