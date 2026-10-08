from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from ..projections.scoring_paces import ScoringPaces


@dataclass( frozen=True )
class PriorYear():
   MIN_GAMES: ClassVar[ int ] = 20

   year: int
   scoring: ScoringPaces
   pim_pace: float | None
   games: int
   nhl_games: int
   age: int
   shots_pace: float | None = None
   arrival: ScoringPaces | None = None


   def age_in_year( self, year: int ) -> int:
      return self.age + year - self.year


   @classmethod
   def reliability( cls, games: int ) -> float:
      if games >= cls.MIN_GAMES:
         return 1.0

      return games / cls.MIN_GAMES
