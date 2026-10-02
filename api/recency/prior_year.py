from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from .prior_source import PriorSource
from ..projections.power_play_pace import PowerPlayPace
from ..projections.scoring_paces import ScoringPaces
from ..projections.season_pace import SeasonPace
from ..projections.short_handed_pace import ShortHandedPace


@dataclass( frozen=True )
class PriorYear():
   MIN_GAMES: ClassVar[ int ] = 20

   year: int
   pace: SeasonPace
   power_play_pace: PowerPlayPace
   short_handed_pace: ShortHandedPace
   pim_pace: float | None
   games: int
   nhl_games: int
   age: float
   playoff_surplus: SeasonPace


   def scoring_paces( self ) -> ScoringPaces:
      return ScoringPaces(
         self.pace.goals,
         self.pace.assists,
         self.power_play_pace.goals,
         self.power_play_pace.assists,
         self.short_handed_pace.goals,
         self.short_handed_pace.assists )


   def source( self ) -> PriorSource:
      if self.nhl_games >= PriorYear.MIN_GAMES:
         return PriorSource.NHL

      return PriorSource.TRANSLATED


   def target_age( self ) -> int:
      return self.age_in_year( self.year + 1 )


   def age_in_year( self, year: int ) -> int:
      return int( self.age ) + year - self.year


   def gap_before( self, year: int ) -> int:
      return year - 1 - self.year
