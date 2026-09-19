from __future__ import annotations

from .career_pace import CareerPace
from ..skater_season import SkaterSeason


class CareerPaceAverager():
   @classmethod
   def average( cls, seasons: list[ SkaterSeason ] ) -> CareerPace:
      count = len( seasons )
      goals = round( sum( season.g_pace for season in seasons ) / count )
      assists = round( sum( season.a_pace for season in seasons ) / count )
      return CareerPace(
         goals=goals,
         assists=assists,
         points=goals + assists )
