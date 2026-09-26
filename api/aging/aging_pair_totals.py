from __future__ import annotations

from dataclasses import dataclass

from .aging_season_paces import AgingSeasonPaces
from ..skaters.skater_season import SkaterSeason


@dataclass( frozen=True )
class AgingPairTotals():
   pair_count: int
   goal_pace: float
   assist_pace: float
   goal_change: float
   assist_change: float


   @classmethod
   def empty( cls ) -> AgingPairTotals:
      return cls( 0, 0.0, 0.0, 0.0, 0.0 )


   def adding(
         self,
         current: SkaterSeason,
         following: SkaterSeason ) -> AgingPairTotals:
      goal_pace, assist_pace = AgingSeasonPaces.resolve( current, following )
      next_goals, next_assists = AgingSeasonPaces.resolve( following, current )
      return AgingPairTotals(
         self.pair_count + 1,
         self.goal_pace + goal_pace,
         self.assist_pace + assist_pace,
         self.goal_change + next_goals - goal_pace,
         self.assist_change + next_assists - assist_pace )


   def percent( self ) -> tuple[ float, float ] | None:
      if self.pair_count == 0 or self.goal_pace == 0 or self.assist_pace == 0:
         return None

      return (
         self.goal_change / self.goal_pace,
         self.assist_change / self.assist_pace )
