from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .prior_source import PriorSource
from ..projections.power_play_pace import PowerPlayPace
from ..projections.season_pace import SeasonPace


@dataclass( frozen=True )
class PriorYear():
   MIN_GAMES: ClassVar[ int ] = 20

   year: int
   pace: SeasonPace
   power_play_pace: PowerPlayPace
   pim_pace: float | None
   games: int
   nhl_games: int
   age: float
   playoff_surplus: SeasonPace


   def source( self ) -> PriorSource:
      if self.nhl_games >= PriorYear.MIN_GAMES:
         return PriorSource.NHL

      return PriorSource.TRANSLATED


   def target_age( self ) -> int:
      return int( self.age ) + 1


   def gap_before( self, year: int ) -> int:
      return year - 1 - self.year
