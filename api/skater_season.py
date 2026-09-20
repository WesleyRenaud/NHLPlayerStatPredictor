from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class SkaterSeason():
   player_id: int
   season_id: int
   age: float
   games_played: int
   goals: int
   assists: int
   points: int
   g_pace: float
   a_pace: float
