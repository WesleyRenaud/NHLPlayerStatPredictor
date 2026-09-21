from __future__ import annotations

from .last_season_skater import LastSeasonSkater


class TeamQualityCalculator():
   @classmethod
   def average( cls, skaters: list[ LastSeasonSkater ] ) -> float | None:
      total = 0.0
      points = 0.0

      for skater in skaters:
         total += skater.games
         points += skater.games * ( skater.pace.goals + skater.pace.assists )

      if not total:
         return None

      return points / total
