from __future__ import annotations

from .career_pace import CareerPace


class TeamPaceAdjuster():
   @classmethod
   def adjust(
         cls,
         pace: CareerPace,
         current: float,
         previous: float ) -> CareerPace:
      delta = current - previous
      return CareerPace(
         goals=pace.goals * ( 1.0 + delta ),
         assists=pace.assists * ( 1.0 + delta ) )
