from __future__ import annotations

from .projection import Projection
from ..skater_season import SkaterSeason


class CareerPaceAverager():
   @classmethod
   def average( cls, seasons: list[ SkaterSeason ] ) -> Projection:
      count = len( seasons )
      goals = round( sum( season.g_pace for season in seasons ) / count )
      assists = round( sum( season.a_pace for season in seasons ) / count )
      return Projection(
         goals=goals,
         assists=assists,
         points=goals + assists )
