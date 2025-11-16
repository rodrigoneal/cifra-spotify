from abc import ABC
from enum import Enum


class Instruments(Enum):
    GUITAR: str = "guitar"
    KEYBOARD: str = "keyboard"
    CAVACO: str = "cavaco"
    UKULELE: str = "ukulele"


class Cifra(ABC):
    async def get_cifra(
        self, singer: str, music: str, instrument: Instruments = Instruments.GUITAR
    ) -> str:
        raise NotImplementedError
