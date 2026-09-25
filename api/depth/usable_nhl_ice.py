from __future__ import annotations

from dataclasses import dataclass

from .club_ice import ClubIce


@dataclass( frozen=True )
class UsableNhlIce():
   season_id: int
   toi: float
   clubs: list[ ClubIce ]
