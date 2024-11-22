from __future__ import annotations
from dataclasses import dataclass

from .states import *
from .global_config import *

@dataclass(frozen=True)
class DownloaderStep():
    CANCELLED: int = 99
    ERROR: int = 98
    IDLE: int = 0
    WAIT: int = 1
    INIT: int = 2
    RUNNING: int = 3
    PROCESSING: int = 4
    DONE: int = 5


@dataclass(frozen=True)
class InteractionModes():
    inline: str = "В чате"
    windowed: str = "Отдельные окна"