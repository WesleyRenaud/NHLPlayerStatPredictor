from __future__ import annotations

from .career_pace import CareerPace
from ..recency_weight import RecencyWeight
from ..season import Season
from ..skater_season import SkaterSeason


class CareerPaceAverager():
   @classmethod
   def average(
         cls,
         seasons: list[ SkaterSeason ],
         weights: list[ RecencyWeight ],
         target_season_id: int ) -> CareerPace:
      by_lag = { weight.lag: weight.weight for weight in weights }
      total = 0.0
      goals_total = 0.0
      assists_total = 0.0

      for season in seasons:
         lag = Season.recency_lag( target_season_id, season.season_id )

         if lag not in by_lag:
            continue

         weight = by_lag[ lag ]
         goals_total += season.g_pace * weight
         assists_total += season.a_pace * weight
         total += weight

      goals = round( goals_total / total )
      assists = round( assists_total / total )
      return CareerPace(
         goals=goals,
         assists=assists,
         points=goals + assists )
