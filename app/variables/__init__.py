from __future__ import annotations
from dataclasses import dataclass

from .states import *
from .global_config import *

class UpdateDBError(Exception):
    pass

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
class SiteAllowed():
    NO: int = 0
    YES: int = 1
    AUTHED: int = 2


@dataclass(frozen=True)
class InteractionModes():
    inline: str = "В чате"
    windowed: str = "Отдельные окна"

@dataclass(frozen=True)
class HashtagsModes():
    no: str = "Нет"
    bf: str = "BooksFine"
    gf: str = "Цокольный этаж"

ACTIVE_SITES_CACHE_KEY = "cache_active_sites"
AUTH_SITES_CACHE_KEY = "cache_sites_with_auth"
USAGE_CACHE_KEY = "cache_usage"
STATS_CACHE_KEY = "cache_stats"
