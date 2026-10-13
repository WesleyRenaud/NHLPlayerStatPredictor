from __future__ import annotations

from dataclasses import dataclass


@dataclass( frozen=True )
class GamesReliability():
   midpoint: int
   reach: int
   odds: float


   @classmethod
   def from_full_season( cls, full_season: int ) -> GamesReliability:
      midpoint = full_season // 2
      reach = midpoint // 2
      short_weight = 1 / 10
      odds = ( 1 - short_weight ) / short_weight
      return cls( midpoint, reach, odds )


   def weight( self, games: int ) -> float:
      steps = ( self.midpoint - games ) / self.reach
      return 1 / ( 1 + self.odds ** steps )
