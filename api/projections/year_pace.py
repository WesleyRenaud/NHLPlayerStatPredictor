from __future__ import annotations

from dataclasses import dataclass

from .season_pace import SeasonPace


@dataclass( frozen=True )
class YearPace():
   pace: SeasonPace
   games: int
