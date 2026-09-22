from __future__ import annotations

from .nhl_lineup_row import NhlLineupRow
from .previous_season_skater import PreviousSeasonSkater


class TeamQualityCalculator():
   @classmethod
   def average( cls, skaters: list[ PreviousSeasonSkater ] ) -> float | None:
      total = 0.0
      points = 0.0

      for skater in skaters:
         total += skater.games
         points += skater.contribution

      if not total:
         return None

      return points / total


   @classmethod
   def total( cls, skaters: list[ NhlLineupRow ] ) -> float:
      points = 0.0

      for skater in skaters:
         points += skater.contribution

      return points
