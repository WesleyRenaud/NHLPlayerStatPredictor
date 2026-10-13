from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .games_reliability import GamesReliability
from ..projections.scoring_paces import ScoringPaces
from ..season import Season


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
      return Season.age_in_year( self.age, self.year, year )


   @classmethod
   def reliability( cls, games: int ) -> float:
      if games >= cls.MIN_GAMES:
         return 1.0

      return GamesReliability.from_full_season( cls.MIN_GAMES ).weight( games )
