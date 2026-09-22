from __future__ import annotations

from .season_pace import SeasonPace


class TeamPaceAdjuster():
   @classmethod
   def adjust(
         cls,
         pace: SeasonPace,
         current: float,
         previous: float ) -> SeasonPace:
      delta = current - previous
      return SeasonPace(
         goals=pace.goals * ( 1.0 + delta ),
         assists=pace.assists * ( 1.0 + delta ) )
