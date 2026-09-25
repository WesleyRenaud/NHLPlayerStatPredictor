from __future__ import annotations

from ..recency.recency_weight import RecencyWeight
from ..season import Season
from .season_pace import SeasonPace
from ..skaters.nhl_skater_season import NhlSkaterSeason


class SeasonPaceAverager():
   @classmethod
   def average(
         cls,
         seasons: list[ NhlSkaterSeason ],
         weights: list[ RecencyWeight ],
         target_season_id: int ) -> SeasonPace:
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

      return SeasonPace(
         goals=goals_total / total,
         assists=assists_total / total )
