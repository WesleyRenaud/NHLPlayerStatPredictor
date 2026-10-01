from __future__ import annotations

from dataclasses import dataclass

from .power_play_pace import PowerPlayPace
from .season_pace import SeasonPace
from .short_handed_pace import ShortHandedPace


@dataclass( frozen=True )
class PaceValues():
   goals: float
   assists: float
   power_play_goals: float
   power_play_assists: float
   short_handed_goals: float
   short_handed_assists: float


   def season_pace( self ) -> SeasonPace:
      return SeasonPace( goals=self.goals, assists=self.assists )


   def power_play_pace( self ) -> PowerPlayPace:
      return PowerPlayPace(
         goals=self.power_play_goals,
         assists=self.power_play_assists )


   def short_handed_pace( self ) -> ShortHandedPace:
      return ShortHandedPace(
         goals=self.short_handed_goals,
         assists=self.short_handed_assists )