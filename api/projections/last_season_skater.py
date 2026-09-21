from __future__ import annotations

from dataclasses import dataclass

from .career_pace import CareerPace


@dataclass( frozen=True )
class LastSeasonSkater():
   player_id: int
   games: float
   pace: CareerPace
