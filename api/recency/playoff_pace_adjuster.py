from __future__ import annotations

from ..projections.season_pace import SeasonPace


class PlayoffPaceAdjuster():
   @classmethod
   def adjust(
         cls,
         pace: SeasonPace,
         surplus: SeasonPace,
         goal_weight: float,
         assist_weight: float ) -> SeasonPace:
      return SeasonPace(
         goals=pace.goals + goal_weight * surplus.goals,
         assists=pace.assists + assist_weight * surplus.assists )
