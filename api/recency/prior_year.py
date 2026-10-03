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
   age: float
   shots_pace: float | None = None


   def age_in_year( self, year: int ) -> int:
      return int( self.age ) + year - self.year
