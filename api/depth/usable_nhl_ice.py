from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .club_ice import ClubIce


@dataclass( frozen=True )
class UsableNhlIce():
   MIN_GAMES: ClassVar[ int ] = 8


   season_id: int
   toi: float
   clubs: list[ ClubIce ]
