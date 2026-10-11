from __future__ import annotations

from dataclasses import dataclass

from ..season import Season
from .skater_position import SkaterPosition


@dataclass( frozen=True )
class SkaterSeason():
   player_id: int
   season_id: int
   age: int
   games_played: int
   goals: int
   assists: int
   points: int
   g_pace: float
   a_pace: float
   position: SkaterPosition


   def age_in_year( self, year: int ) -> int:
      return Season.age_in_year( self.age, Season.start_year( self.season_id ), year )
